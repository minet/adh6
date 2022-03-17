import click
from flask import Flask, cli
from sqlalchemy.engine.create import create_engine
from src.constants import MembershipDuration, MembershipStatus
import uuid
from datetime import date, datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from common import init
from faker import Faker

import ipaddress
from src.use_case.decorator.security import Roles
from src.interface_adapter.sql.model.models import ApiKey, db, Adherent, AccountType, Adhesion, Membership, Modification, PaymentMethod, Routeur, Transaction, Vlan, Switch, Port, Chambre, Caisse, Account, Device, Product
application = init()
assert application.app is not None, "No flask application"
manager: Flask = application.app

@manager.cli.command("check_subnet")
def check_subnet():
    public_range = ipaddress.IPv4Network("157.159.192.0/22").address_exclude(ipaddress.IPv4Network("157.159.195.0/24"))
    excluded_addresses = ["157.159.192.0", "157.159.192.1", "157.159.192.255", "157.159.193.0", "157.159.193.1", "157.159.193.255", "157.159.194.0", "157.159.194.1", "157.159.194.255"]
    hosts = []
    for r in public_range:
        hosts.extend(list(r.hosts()))
    private_range = ipaddress.IPv4Network("10.42.0.0/16").subnets(new_prefix=28)
    mappings = {}
    for subnet, ip in zip(private_range, hosts):
        if str(ip) in excluded_addresses:
            continue
        mappings[str(subnet)] = str(ip)

    session: Session = db.session
    adherents: List[Adherent] = session.query(Adherent).all()
    i = 1
    for a in adherents:
        if a.date_de_depart is None:
            # print(f'{a.login}: Has no departure date')
            continue
        if a.ip is None or a.subnet is None:
            continue
        if a.date_de_depart < date.today() and a.subnet is not None and a.subnet != "":
            print(f'{a.login}: Should not have any subnet')
            continue
        if a.ip is None:
            continue
        if a.subnet not in mappings:
            print(f'{a.login}: {a.ip} is not in the mapping')
            continue
        if a.ip != mappings[a.subnet]:
            i += 1
            print(f'{a.login}: {a.subnet} is not in mapped to {a.ip} but to {mappings[a.subnet]}')
    print(i)

limit_departure_date = date(2019, 1, 1)
@manager.cli.command("remove_member")
def remove_members():
    session: Session = db.session
    adherents: List[Adherent] = session.query(Adherent).filter(Adherent.date_de_depart <= limit_departure_date).all()

    passed_adherents: List[Adherent] = []
    total = len(adherents)
    total_lines = 0
    deleted_devices = 0
    deleted_modifications = 0
    for i, a in enumerate(adherents):
        print(f'{i}/{total}: {a.login}, {a.created_at}')
        accounts: List[Account] = session.query(Account).filter(Account.adherent_id == a.id).all()
        pass_adherent = False
        for acc in accounts:
            transactions: List[Transaction] = session.query(Transaction).filter(Transaction.src == acc.id).all()
            transactions_from: List[Transaction] = session.query(Transaction).filter(Transaction.author_id == a.id).all()
            if len(transactions) != 0 or len(transactions_from) != 0:
                print("Adherent passed")
                passed_adherents.append(a)
                pass_adherent = True
                continue
            session.delete(acc)
            total_lines += 1
        if pass_adherent:
            continue
        devices: List[Device] = session.query(Device).filter(Device.adherent_id == a.id).all()
        for d in devices:
            session.delete(d)
            total_lines += 1
            deleted_devices += 1
        adhesions: List[Adhesion] = session.query(Adhesion).filter(Adhesion.adherent_id == a.id).all()
        for add in adhesions:
            session.delete(add)
            total_lines += 1
        routeurs: List[Routeur] = session.query(Routeur).filter(Routeur.adherent_id == a.id).all()
        for r in routeurs:
            session.delete(r)
            total_lines += 1
        modifications: List[Modification] = session.query(Modification).filter(Modification.adherent_id == a.id).all()
        for m in modifications:
            session.delete(m)
            total_lines += 1
            deleted_modifications += 1
        session.delete(a)
    print(f'deleted lines: {total_lines}, ')
    session.commit()
   
@manager.cli.command("check_transactions_member_to_remove")
def check_transactions_member_to_remove():
    session: Session = db.session
    adherents: List[Adherent] = session.query(Adherent).filter(Adherent.date_de_depart <= limit_departure_date).all()

    total = len(adherents)
    for i, a in enumerate(adherents):
        print(f'{i}/{total}: {a.login}, {a.created_at}')
        devices: List[Device] = session.query(Device).filter(Device.adherent_id == a.id).all()
        for d in devices:
            session.delete(d)
        adhesions: List[Adhesion] = session.query(Adhesion).filter(Adhesion.adherent_id == a.id).all()
        for add in adhesions:
            session.delete(add)
        routeurs: List[Routeur] = session.query(Routeur).filter(Routeur.adherent_id == a.id).all()
        for r in routeurs:
            session.delete(r)
        accounts: List[Account] = session.query(Account).filter(Account.adherent_id == a.id).all()
        for acc in accounts:
            print(acc.id)
            transactions: List[Transaction] = session.query(Transaction).filter(Transaction.src == acc.id).all() + session.query(Transaction).filter(Transaction.author_id == a.id).all()
            for t in transactions:
                print(a.id)
                print(t.name)
    session.commit() 

@manager.cli.command("generate_membership")
def generate_membership():
    session: Session = db.session
    adherents: List[Adherent] = session.query(Adherent).filter(Adherent.date_de_depart >= limit_departure_date).all()
    products: Dict[str, Product] = {}
    products_sql = session.query(Product).all()
    for p in products_sql:
        products[p.name] = p

    for adherent in adherents:
        print(adherent.login)
        memberships: List[Membership] = session.query(Membership).filter(Membership.adherent_id == adherent.id).all()
        if memberships != []:
            print("Already have a membership")
            continue
        membership: Membership = Membership(
            uuid=str(uuid.uuid4()),
            account_id=None,
            create_at=adherent.created_at,
            has_room=False,
            duration=MembershipDuration.NONE,
            first_time=False,
            adherent_id=adherent.id,
            payment_method_id=None,
            products="",
            status=MembershipStatus.COMPLETE,
            update_at=adherent.created_at,

        )
        account = session.query(Account).filter(Account.adherent_id == adherent.id).one_or_none()
        if account is None:
            print("No Account")
            session.add(membership)
            continue
        membership.account_id = account.id
        transactions: List[Transaction] = session.query(Transaction).filter(Transaction.src == account.id).all()
        if not transactions:
            print("Empty Account")
            session.add(membership)
            continue
        grouped_transactions: Dict[date, List[Transaction]] = {}
        first_date: Optional[date] = None
        for transaction in transactions:
            if first_date is None or first_date > transaction.timestamp.date():
                first_date = transaction.timestamp.date()
            if transaction.timestamp.date() not in grouped_transactions:
                grouped_transactions[transaction.timestamp.date()] = [transaction]
            else:
                grouped_transactions[transaction.timestamp.date()].append(transaction)

        for d, ts in grouped_transactions.items():
            print(d)
            current_products: List[int] = []
            membership: Membership = Membership(
                uuid=str(uuid.uuid4()),
                account_id=account.id,
                create_at=adherent.created_at,
                has_room=False,
                duration=MembershipDuration.NONE,
                first_time=False,
                adherent_id=adherent.id,
                payment_method_id=None,
                products="",
                status=MembershipStatus.COMPLETE,
                update_at=adherent.created_at,
            )
            for t in ts:
                if membership.duration == MembershipDuration.NONE:
                    membership.create_at = t.timestamp
                    membership.update_at = t.timestamp
                    membership.first_time = t.timestamp.date() == first_date
                    if t.name.startswith('Internet'):
                        membership.has_room = True
                        membership.create_at = t.timestamp
                        membership.update_at = t.timestamp
                        membership.first_time = t.timestamp.date() == first_date
                        if t.name.endswith('1 mois'):
                            membership.duration = MembershipDuration.ONE_MONTH
                        if t.name.endswith('2 mois'):
                            membership.duration = MembershipDuration.TWO_MONTH
                        if t.name.endswith('3 mois'):
                            membership.duration = MembershipDuration.THREE_MONTH
                        if t.name.endswith('4 mois'):
                            membership.duration = MembershipDuration.FOUR_MONTH
                        if t.name.endswith('5 mois'):
                            membership.duration = MembershipDuration.FIVE_MONTH
                        if t.name.endswith('6 mois'):
                            membership.duration = MembershipDuration.SIX_MONTH
                        if t.name.endswith('1 an'):
                            membership.duration = MembershipDuration.ONE_YEAR
                        if t.name.endswith('sans chambre'):
                            membership.has_room = False
                            membership.duration = MembershipDuration.ONE_YEAR
                        print(membership.duration)
                if t.name in products:
                    current_products.append(products[t.name].id)
            membership.products = str(current_products) if current_products != [] else ""
            session.add(membership)
    session.commit()

@manager.cli.command("reset_membership")
def reset_membership():
    session: Session = db.session
    memberships: List[Membership] = session.query(Membership).all()
    for m in memberships:
        print(m.uuid)
        session.delete(m)
    session.commit()

@manager.cli.command("check_migration_from_adh5")
def check_migration_from_adh5():
    engine = create_engine('')
    session: Session = db.session
    i = 0
    j = 0
    total = 0
    adherents: List[Adherent] = session.query(Adherent).filter(Adherent.date_de_depart >= limit_departure_date).all()
    with open("migration_transactions.md", "w+") as f:
        f.writelines(["# Missing Transactions\n"])
        for adherent in adherents:
            # Check an account exist, if not create a fake one (for now)
            account: Account = session.query(Account).filter(Account.adherent_id == adherent.id).one_or_none()
            if account is None:
                print("Creation of an account")
                account = Account(
                    type=2,
                    creation_date=adherent.created_at,
                    name=f'{adherent.prenom} {adherent.nom.upper()} ({adherent.login})',
                    actif=True,
                    compte_courant=False,
                    pinned=False,
                    adherent_id=adherent.id
                )
                session.add(account)
                session.flush()
            
            transactions: List[Transaction] = session.query(Transaction).filter(Transaction.src == account.id).all()
            adh5_transactions: List[Transaction] = []
            with engine.connect() as connection:
                adh5_adherents = connection.execute("SELECT id FROM adherents WHERE login='{}'".format(adherent.login))
                adh5_adherent_id = 0
                for row in adh5_adherents:
                    adh5_adherent_id = row['id']
                
                ecritures = connection.execute("SELECT * FROM ecritures WHERE adherent_id={} AND created_at >= '{}'".format(adh5_adherent_id, datetime(2020, 2, 15)))
                for e in ecritures:
                    adh5_transactions.append(Transaction(
                        value=e['montant'],
                        timestamp=e['date'],
                        src=account.id,
                        dst=1,
                        name=e['intitule'],
                        attachments="",
                        type=e['moyen'],
                        author_id=adherent.id,
                        pending_validation=False
                    ))
            if len(adh5_transactions) == 0:
                continue
            missing_transactions: List[Transaction] = []
            for adh5_t in adh5_transactions:
                if len(transactions) == 0:
                    missing_transactions.append(adh5_t)
                    continue
                in_adh6 = False
                for t in transactions:
                    if adh5_t.name == t.name and adh5_t.timestamp.date() == t.timestamp.date():
                        in_adh6 = True
                        break
                if not in_adh6:
                    missing_transactions.append(adh5_t)
            j += len(missing_transactions)
            if len(missing_transactions) == 0:
                continue
            f.writelines([f"## {adherent.login}\n", "|*Name*|*Timestamp*|*Value*|\n", "|:-:|:-:|:-:|\n"])
            sum_adh = 0
            print(adherent.login)
            for t in missing_transactions:
                total += t.value
                print("{}, {}, {}".format(t.name, t.timestamp, t.value))
                f.write("|{}|{}|{}|\n".format(t.name, t.timestamp, t.value))
                sum_adh += t.value
            f.write("|||*{}*|\n".format(sum_adh))
            i += 1
        print(f'{i} adherent, {j} transactions, {total} €')


@manager.cli.command("api_key")
@click.argument("login")
def api_key(login: str = "dev-api-key"):
    """Add seed data to the database."""
    session: Session = db.session

    print("Generate api key")
    api_key = (str(uuid.uuid4()), login, Roles.SUPERADMIN.value)
    session.add(
        ApiKey(
            uuid=api_key[0],
            name=api_key[1],
            role=api_key[2]
        )
    )
    session.commit()
    print(f"generated key: {api_key[0]}")


@manager.cli.command("seed")
def seed():
    """Add seed data to the database."""
    session: Session = db.session

    print("Seeding account types")
    account_types = [1,"Special"],[2,"Adherent"],[3,"Club interne"],[4,"Club externe"],[5,"Association externe"]
    session.bulk_save_objects([
        AccountType(
            id=e[0],
            name=e[1]
        ) for e in account_types
    ])

    print("Seeding MiNET accounts")
    accounts = [1, 1, "MiNET frais techniques", True, None, True, True],[2, 1, "MiNET frais asso", True, None, True, True]
    session.bulk_save_objects([
        Account(
            id=e[0],
            type=e[1],
            name=e[2],
            actif=e[3],
            adherent_id=e[4],
            compte_courant=e[5],
            pinned=e[6]
        ) for e in accounts
    ])

    print("Seeding Products")
    products = [1,"Cable 3m", 3, 3],[2,"Cable 5m", 5, 5],[3,"Adaptateur USB/Ethernet", 13.00, 13.00],[4,"Adaptateur USB-C/Ethernet", 12.00, 12.00]
    session.bulk_save_objects([
        Product(
            id=e[0],
            name=e[1],
            buying_price=e[2],
            selling_price=e[3]
        ) for e in products
    ])

    print("Seeding payment methods")
    payment_methods = [1,"Liquide"],[2,"Chèque"],[3,"Carte bancaire"],[4,"Virement"],[5,"Stripe"]
    session.bulk_save_objects([
        PaymentMethod(
            id=e[0],
            name=e[1]
        ) for e in payment_methods
    ])

    print("Seeding cashbox")
    session.add(Caisse(
        fond=0,
        coffre=0
    ))

    print("Seeding vlans")
    vlans = [41, "157.159.41.0/24", "2001:660:3203:401::/64", "157.159.41.1/32", ""], [35, "10.42.0.0/16", "", "", ""], [36, "157.159.192.0/22", "", "157.159.195.0/24", ""], [30, "172.30.0.0/16", "", "", ""]
    session.bulk_save_objects([
        Vlan(
            numero=e[0], 
            adresses=e[1], 
            adressesv6=e[2], 
            excluded_addr=e[3], 
            excluded_addrv6=e[4]
        ) for e in vlans
    ])

    print("Seeding Rooms")
    session.bulk_save_objects([
        Chambre(
            id=i,
            numero=i,
            description="Chambre " + str(i),
            vlan_id=1
        ) for i in range(1, 30)
    ])

    print("Seeding Switchs")
    switchs = [1, "Switch local", "192.168.102.219", "adh5"],
    session.bulk_save_objects([
        Switch(
            id=e[0],
            description=e[1],
            ip=e[2],
            communaute=e[3],
        ) for e in switchs
    ])

    print("Seeding 30 Ports Switch local + link to room")
    session.bulk_save_objects([
        Port(
            rcom=0,
            numero="1/0/" + str(i),
            oid="1010" + str(i),
            switch_id=1,
            chambre_id=i
        ) for i in range(1, 30)
    ])

    session.commit()


@manager.cli.command("fake")
@click.argument("login")
def fake(login):
    """Add dummy data to the database."""
    fake = Faker()
    session: Session = db.session

    import datetime as dt

    now = datetime.now()
    adherent = Adherent(
        nom=fake.last_name_nonbinary(),
        prenom=fake.first_name_nonbinary(),
        mail=fake.email(),
        login=login,
        ldap_login=login,
        password="",
        chambre_id=1,
        datesignedminet=now,
        date_de_depart=now + dt.timedelta(days=365),
        subnet="10.0.42.0/28",
        ip="157.159.192.2"
    )

    session.add(adherent)

    account = Account(
        type=2,
        name=adherent.nom + " " + adherent.prenom,
        actif=True,
        compte_courant=False,
        pinned=False,
        adherent=adherent
    )

    session.add(account)

    session.add(Transaction(
        value=9,
        timestamp=now,
        src_account=account,
        dst=2,
        name="Internet - 1 an",
        attachments="",
        type=3,
        author_id=1,
        pending_validation=False,
    ))
    session.add(Transaction(
        value=41,
        timestamp=now,
        src_account=account,
        dst=1,
        name="Internet - 1 an",
        attachments="",
        type=3,
        author_id=1,
        pending_validation=False,
    ))
    
    for _ in range(1, 4):
        session.add(Device(
            mac=fake.mac_address(),
            ip=None,
            adherent=adherent,
            ipv6=None,
            type=0
        ))
    for _ in range(1, 4):
        session.add(Device(
            mac=fake.mac_address(),
            ip=None,
            adherent=adherent,
            ipv6=None,
            type=1
        ))
    session.commit()



if __name__ == '__main__':
    application.run()
