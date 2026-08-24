import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from adh6 import mail
from adh6.config.configuration import settings
from adh6.context import get_api_key_id
from adh6.decorator import log_call
from adh6.default import CRUDManager
from adh6.entity import AbstractTransaction, PaymentMethod
from adh6.exceptions import ProductNotFoundError
from adh6.member.interfaces import MemberRepository
from adh6.treasury.interfaces import PaymentMethodRepository, ProductRepository
from adh6.treasury.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)

# The container clock is UTC; a treasury mail read in Évry must not be dated the day before.
PARIS = ZoneInfo("Europe/Paris")


class ProductManager(CRUDManager):
    def __init__(
        self,
        product_repository: ProductRepository,
        transaction_manager: TransactionManager,
        payment_method_repository: PaymentMethodRepository,
        member_repository: MemberRepository,
    ):
        super().__init__(product_repository, ProductNotFoundError)  # type: ignore
        self.transaction_manager = transaction_manager
        self.payment_method_repository = payment_method_repository
        self.product_repository = product_repository
        # Needed to name the buyer and the seller in the treasury notice. treasury already
        # depends on member elsewhere -- see export_manager -- so this adds no new coupling.
        self.member_repository = member_repository

    @log_call
    async def buy(self, member_id: int, payment_method_id: int, author_id: int, product_ids: list[int] = []) -> None:
        if not product_ids:
            raise ProductNotFoundError("None")

        payment_method = await self.payment_method_repository.get_by_id(payment_method_id)

        sold: list[dict[str, object]] = []
        for product_id in product_ids:
            product = await self.product_repository.get_by_id(product_id)
            if not product:
                raise ProductNotFoundError(product_id)

            await self.transaction_manager.update_or_create(
                AbstractTransaction(
                    name=product.name,
                    value=product.selling_price,
                    paymentMethod=payment_method.id,  # type: ignore
                    author=author_id,
                    apiKeyId=get_api_key_id(),
                    productType="product",
                    productId=product_id,
                )
            )
            # stock_after stays None until the stock column exists -- see plan/04. The template
            # simply omits the mention rather than showing a wrong number.
            sold.append({"name": product.name, "price": f"{product.selling_price:.2f}", "stock_after": None})

        await self._notify_treasury(member_id, author_id, payment_method, sold)

    async def _notify_treasury(
        self,
        member_id: int,
        author_id: int,
        payment_method: PaymentMethod | None,
        sold: list[dict[str, object]],
    ) -> None:
        """One mail per checkout, not one per item: the screen lets several products be ticked.

        Never raises: a delivery failure must not undo a sale that is already recorded.
        """
        if not settings.treasury_recipients:
            return
        try:
            buyer = await self.member_repository.get_by_id(member_id)
            seller = await self.member_repository.get_by_id(author_id)
            total = sum(float(str(item["price"])) for item in sold)
            await mail.send_purchase_admin_async(
                to=settings.treasury_recipients,
                username=buyer.username if buyer else str(member_id),
                adh6_url=f"https://{settings.adh6_url}/fr/member/view/{member_id}/payment",
                items=sold,
                total=f"{total:.2f}",
                payment_method=payment_method.name if payment_method else "-",
                author=seller.username if seller else str(author_id),
                paid_at=datetime.now(PARIS),
            )
        except Exception:
            logger.warning("Cannot notify the treasury of the purchase by member %s", member_id, exc_info=True)
