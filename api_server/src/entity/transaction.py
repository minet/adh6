# coding=utf-8
from dataclasses import dataclass

from src.entity.account import Account
from src.entity.admin import Admin
from src.entity.member import Member
from src.entity.payment_method import PaymentMethod


@dataclass
class Transaction:
    src: Account
    dst: Account
    name: str
    value: str
    timestamp: str
    attachments: str
    paymentMethod: PaymentMethod
    author: Admin
