# coding=utf-8
# Import necessary modules and classes
from typing import List
from adh6.entity import AbstractAccount, AbstractTransaction
from adh6.decorator import log_call
from adh6.constants import KnownAccountExpense
from adh6.exceptions import AccountNotFoundError, ProductNotFoundError
from adh6.default import CRUDManager

# Import custom interfaces
from adh6.treasury.interfaces import ProductRepository, AccountRepository, PaymentMethodRepository
from adh6.treasury import TransactionManager

# Define a class for managing products and transactions related to them
class ProductManager(CRUDManager):
    
    # Initialize the class with repositories for managing products, transactions, payment methods, and accounts
    def __init__(self, 
                 product_repository: ProductRepository, 
                 transaction_manager: TransactionManager,
                 payment_method_repository: PaymentMethodRepository,
                 account_repository: AccountRepository):
        # Call the parent class's __init__ method to set up basic CRUD functionality for the product repository
        super().__init__(product_repository, ProductNotFoundError)
        # Set the remaining repositories as attributes of the class
        self.transaction_manager = transaction_manager
        self.payment_method_repository = payment_method_repository
        self.product_repository = product_repository
        self.account_repository = account_repository

    # Define a method for buying products
    @log_call
    def buy(self, member_id: int, payment_method_id: int, product_ids: List[int] = []) -> None:
        # If no product IDs are provided, raise an error
        if not product_ids:
            raise ProductNotFoundError("None")

        # Retrieve the payment method object from the payment method repository
        payment_method = self.payment_method_repository.get_by_id(payment_method_id)

        # Search for the technical expense account using the account repository
        dst_accounts, _ = self.account_repository.search_by(limit=1, filter_=AbstractAccount(name=KnownAccountExpense.TECHNICAL_EXPENSE.value))
        # If the account is not found, raise an error
        if not dst_accounts:
            raise AccountNotFoundError(KnownAccountExpense.TECHNICAL_EXPENSE.value)

        # Search for the member's account using the account repository
        src_accounts, _ = self.account_repository.search_by(limit=1, filter_=AbstractAccount(member=member_id))
        # If the account is not found, raise an error
        if not src_accounts:
            raise AccountNotFoundError(KnownAccountExpense.TECHNICAL_EXPENSE.value)

        # Loop through each product ID and create a transaction for each one
        for i in product_ids:
            # Retrieve the product object from the product repository
            product = self.product_repository.get_by_id(i)

            # Create a new transaction object using the transaction repository
            _ = self.transaction_manager.update_or_create(
                AbstractTransaction(
                    src=src_accounts[0].id,
                    dst=dst_accounts[0].id,
                    name=product.name,
                    value=product.selling_price,
                    payment_method=payment_method.id,
                ))
