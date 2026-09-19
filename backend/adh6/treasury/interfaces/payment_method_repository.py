from adh6.default.crud_repository import CRUDRepository
from adh6.entity import PaymentMethod


class PaymentMethodRepository(CRUDRepository[PaymentMethod, PaymentMethod, int]):
    pass  # pragma: no cover
