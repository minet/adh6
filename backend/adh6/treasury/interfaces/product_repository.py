import abc

from adh6.constants import DEFAULT_LIMIT, DEFAULT_OFFSET
from adh6.entity import AbstractProduct, Product


class ProductRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, object_id: int) -> Product | None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def search_by(
        self, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, terms: str | None = None
    ) -> tuple[list[Product], int]:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def create(self, abstract_product: AbstractProduct) -> Product:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def update(self, abstract_product: AbstractProduct, product_id: int) -> None:
        pass  # pragma: no cover

    @abc.abstractmethod
    async def delete(self, product_id: int) -> None:
        pass  # pragma: no cover
