from adh6.context import get_api_key_id
from adh6.decorator import log_call
from adh6.default import CRUDManager
from adh6.entity import AbstractTransaction
from adh6.exceptions import ProductNotFoundError
from adh6.treasury.interfaces import PaymentMethodRepository, ProductRepository
from adh6.treasury.transaction_manager import TransactionManager


class ProductManager(CRUDManager):
    def __init__(
        self,
        product_repository: ProductRepository,
        transaction_manager: TransactionManager,
        payment_method_repository: PaymentMethodRepository,
    ):
        super().__init__(product_repository, ProductNotFoundError)  # type: ignore
        self.transaction_manager = transaction_manager
        self.payment_method_repository = payment_method_repository
        self.product_repository = product_repository

    @log_call
    async def buy(self, member_id: int, payment_method_id: int, author_id: int, product_ids: list[int] = []) -> None:
        if not product_ids:
            raise ProductNotFoundError("None")

        payment_method = await self.payment_method_repository.get_by_id(payment_method_id)

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
