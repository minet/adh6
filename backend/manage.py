import ipaddress
import uuid
from datetime import date, datetime

import click
from adh6.authentication import AuthenticationMethod, Roles
from adh6.authentication.storage.models import ApiKey, AuthenticationRoleMapping
from adh6.constants import MembershipDuration, MembershipStatus
from adh6.device.storage.models import Device
from adh6.member.storage.models import Adherent, Membership, NotificationTemplate
from adh6.network.storage.models import Port, Switch
from adh6.room.storage.models import Chambre
from flask import Flask
from flask_alembic import Alembic
from sqlalchemy.orm import Session
from adh6.storage import Base
from adh6.subnet.storage.models import Vlan
from adh6.treasury.storage.models import (
    Account,
    AccountType,
    Caisse,
    PaymentMethod,
    Product,
)  # , Transaction
from faker import Faker

# from adh6.storage.sql.models import Adhesion, Modification, Routeur

# Create a minimal Flask app for CLI commands and Alembic migrations
manager = Flask(__name__)
manager.config.from_object("adh6.config.configuration.Config")

alembic = Alembic(manager, metadatas=Base.metadata)  # add alembic CLI options
# nb: alembic is only available in the CLI, because it only supports synchronous sqlalchemy, and when using uvicorn the app is async


# TODO: Refactor to use async session when async CLI support is available
# @manager.cli.command("check_subnet")
# def check_subnet():
#     # TODO: documenter cette fonction, ce qu'elle fait, et si elle est encore utile
#     public_range = ipaddress.IPv4Network("157.159.192.0/22").address_exclude(ipaddress.IPv4Network("157.159.195.0/24"))
#     excluded_addresses = [
#         "157.159.192.0",
#         "157.159.192.1",
#         "157.159.192.255",
#         "157.159.193.0",
#         "157.159.193.1",
#         "157.159.193.255",
#         "157.159.194.0",
#         "157.159.194.1",
#         "157.159.194.255",
#     ]
#     hosts = []
#     for r in public_range:
#         hosts.extend(list(r.hosts()))
#     private_range = ipaddress.IPv4Network("10.42.0.0/16").subnets(new_prefix=28)
#     mappings = {}
#     for subnet, ip in zip(private_range, hosts):
#         if str(ip) in excluded_addresses:
#             continue
#         mappings[str(subnet)] = str(ip)
#
#     session: Session = db.session
#     adherents: list[Adherent] = session.query(Adherent).all()
#     i = 1
#     for a in adherents:
#         if a.date_de_depart is None:
#             # print(f'{a.login}: Has no departure date')
#             continue
#         if a.ip is None or a.subnet is None:
#             continue
#         if a.date_de_depart < date.today() and a.subnet is not None and a.subnet != "":
#             print(f"{a.login}: Should not have any subnet")
#             continue
#         if a.ip is None:
#             continue
#         if a.subnet not in mappings:
#             print(f"{a.login}: {a.ip} is not in the mapping")
#             continue
#         if a.ip != mappings[a.subnet]:
#             i += 1
#             print(f"{a.login}: {a.subnet} is not in mapped to {a.ip} but to {mappings[a.subnet]}")
#     print(i)


# limit_departure_date = date(2019, 1, 1)


# @manager.cli.command("remove_member")
# def remove_members():
#     # TODO: documenter cette fonction, ce qu'elle fait, et si elle est encore utile
#     session: Session = db.session
#     adherents: list[Adherent] = session.query(Adherent).filter(Adherent.date_de_depart <= limit_departure_date).all()

#     passed_adherents: list[Adherent] = []
#     total = len(adherents)
#     total_lines = 0
#     deleted_devices = 0
#     deleted_modifications = 0
#     for i, a in enumerate(adherents):
#         print(f"{i}/{total}: {a.login}, {a.created_at}")
#         accounts: list[Account] = session.query(Account).filter(Account.adherent_id == a.id).all()
#         pass_adherent = False
#         for acc in accounts:
#             transactions: list[Transaction] = session.query(Transaction).filter(Transaction.src == acc.id).all()
#             transactions_from: list[Transaction] = (
#                 session.query(Transaction).filter(Transaction.author_id == a.id).all()
#             )
#             if len(transactions) != 0 or len(transactions_from) != 0:
#                 print("Adherent passed")
#                 passed_adherents.append(a)
#                 pass_adherent = True
#                 continue
#             session.delete(acc)
#             total_lines += 1
#         if pass_adherent:
#             continue
#         devices: list[Device] = session.query(Device).filter(Device.adherent_id == a.id).all()
#         for d in devices:
#             session.delete(d)
#             total_lines += 1
#             deleted_devices += 1
#         adhesions: list[Adhesion] = session.query(Adhesion).filter(Adhesion.adherent_id == a.id).all()
#         for add in adhesions:
#             session.delete(add)
#             total_lines += 1
#         routeurs: list[Routeur] = session.query(Routeur).filter(Routeur.adherent_id == a.id).all()
#         for r in routeurs:
#             session.delete(r)
#             total_lines += 1
#         modifications: list[Modification] = session.query(Modification).filter(Modification.adherent_id == a.id).all()
#         for m in modifications:
#             session.delete(m)
#             total_lines += 1
#             deleted_modifications += 1
#         session.delete(a)
#     print(f"deleted lines: {total_lines}, ")
#     session.commit()


# @manager.cli.command("check_transactions_member_to_remove")
# def check_transactions_member_to_remove():
#     session: Session = db.session
#     adherents: list[Adherent] = session.query(Adherent).filter(Adherent.date_de_depart <= limit_departure_date).all()

#     total = len(adherents)
#     for i, a in enumerate(adherents):
#         print(f"{i}/{total}: {a.login}, {a.created_at}")
#         devices: list[Device] = session.query(Device).filter(Device.adherent_id == a.id).all()
#         for d in devices:
#             session.delete(d)
#         adhesions: list[Adhesion] = session.query(Adhesion).filter(Adhesion.adherent_id == a.id).all()
#         for add in adhesions:
#             session.delete(add)
#         routeurs: list[Routeur] = session.query(Routeur).filter(Routeur.adherent_id == a.id).all()
#         for r in routeurs:
#             session.delete(r)
#         accounts: list[Account] = session.query(Account).filter(Account.adherent_id == a.id).all()
#         for acc in accounts:
#             print(acc.id)
#             transactions: list[Transaction] = (
#                 session.query(Transaction).filter(Transaction.src == acc.id).all()
#                 + session.query(Transaction).filter(Transaction.author_id == a.id).all()
#             )
#             for t in transactions:
#                 print(a.id)
#                 print(t.name)
#     session.commit()


# NOTE: CLI seed and test data generation commands have been disabled during migration to async.
# These will need to be rewritten to use AsyncSession when Flask CLI async support is available.
# For now, use the FastAPI API endpoints directly to seed data or use database migrations.
# TODO: Implement async seed/fake commands using asyncio and AsyncSession


if __name__ == "__main__":
    manager.run()
