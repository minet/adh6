# coding=utf-8
"""
Treasury repository.
"""
import abc
from typing import List

from src.entity import AbstractTransaction
from src.entity.transaction import Transaction


class TransactionRepository(metaclass=abc.ABCMeta):
    """
    Abstract interface to handle devices.
    """

    @abc.abstractmethod
    def search_transaction_by(self, ctx, limit=None, offset=None, terms=None, filter_: AbstractTransaction = None) -> \
            (List[Transaction], int):
        """
        Search for a transaction.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def create_transaction(self, ctx, author=None, abstract_transaction: AbstractTransaction = None):
        """
        Create a transaction.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def update_transaction(self, ctx, transaction_to_update, attachments=None, pending_validation=False):
        """
        Update a transaction to add an invoice.

        :raise TransactionNotFound
        """
        pass  # pragma: no cover
