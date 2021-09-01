from src.constants import MembershipDuration, MembershipStatus
import uuid
import itertools
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from common import init
from flask_script import Manager
from flask_migrate import MigrateCommand
from faker import Faker

from src.interface_adapter.sql.model.database import Database
from src.interface_adapter.sql.model.models import Adherent, AccountType, Membership, PaymentMethod, Transaction, Vlan, Switch, Port, Chambre, \
    Admin, Caisse, Account, Device, Product

application, migrate = init(testing=False, managing=True)

manager = Manager(application.app)
manager.add_command('db', MigrateCommand)

limit_departure_date = date(2019, 1, 1)
limit_creation_date = date(2017, 1, 1)
@manager.command
def remove_duplicate_accounts():
    s: Session = Database.get_db().get_session()
    adherents: List[Adherent] = s.query(Adherent).filter(Adherent.created_at >= limit_creation_date).filter(Adherent.date_de_depart >= limit_departure_date).all()
    
    for adherent in adherents:
        print(adherent.login)
        accounts: List[Account] = s.query(Account).filter(Account.adherent_id == adherent.id).order_by(Account.id).all()
        if len(accounts) == 0:
            print("No Account")
            continue
        if len(accounts) == 1:
            continue
        empty_accounts: List[Account] = []
        for account in accounts:
            t = s.query(Transaction).filter(Transaction.src == account.id).all()
            if not t:
                empty_accounts.append(account)
        if len(accounts) == len(empty_accounts):
            empty_accounts.pop(0)
        for a in accounts:
            s.delete(a)
    s.commit()

@manager.command
def generate_membership():
    s: Session = Database.get_db().get_session()
    adherents: List[Adherent] = s.query(Adherent).filter(Adherent.created_at >= limit_creation_date).filter(Adherent.date_de_depart >= limit_departure_date).all()
    products: Dict[str, Product] = {}
    products_sql = s.query(Product).all()
    for p in products_sql:
        products[p.name] = p

    for adherent in adherents:
        print(adherent.login)
        memberships: List[Membership] = s.query(Membership).filter(Membership.adherent_id == adherent.id).all()
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
        account = s.query(Account).filter(Account.adherent_id == adherent.id).one_or_none()
        if account is None:
            print("No Account")
            s.add(membership)
            continue
        membership.account_id = account.id
        transactions: List[Transaction] = s.query(Transaction).filter(Transaction.src == account.id).all()
        if not transactions:
            print("Empty Account")
            s.add(membership)
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
        
        DURATION_STRING = {
        -1: 'sans chambre',
        1: '1 mois',
        2: '2 mois',
        3: '3 mois',
        4: '4 mois',
        5: '5 mois',
        6: '6 mois',
        12: '1 an',
        }

        current_products: List[int] = []
        for d, ts in grouped_transactions.items():
            print(d)
            for t in ts:
                if membership.duration is None:
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
                if t.name in products:
                    current_products.append(products[t.name].id)
            membership.products = str(current_products) if current_products != [] else ""
            s.add(membership)
    s.commit()

@manager.command
def todays_subscriptions():
    s: Session = Database.get_db().get_session()
    now = datetime.today()
    today = now + timedelta(-1)
    tomorrow = now
    adherents: List[Adherent] = s.query(Adherent).filter(Adherent.created_at >= limit_creation_date).filter(Adherent.date_de_depart >= limit_departure_date).filter(Adherent.updated_at <= tomorrow, Adherent.updated_at >= today).all()
    with open("memberships.md", "w+") as f:
        f.writelines(["|#|Login|Create At|Update At|Account Name|First time|Duration|Transaction Name|Transaction Timestamp|\n", "|-|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"])
        for i, adherent in enumerate(adherents):
            print(adherent.login)
            account: Account = s.query(Account).filter(Account.adherent_id == adherent.id).one_or_none()
            if account is None:
                f.writelines(f'|{i}|{adherent.login}|{adherent.created_at}|{adherent.updated_at}|None|None|None|None|None|\n')
                continue
            memberships: List[Membership] = s.query(Membership).filter(Membership.adherent_id == adherent.id).all()
            if not memberships:
                f.writelines(f'|{i}|{adherent.login}|{adherent.created_at}|{adherent.updated_at}|{account.name}|None|None|None|None|\n')
                continue
            transactions: List[Transaction] = s.query(Transaction).filter(Transaction.src == account.id).order_by(Transaction.timestamp.desc()).all()
            if not transactions:
                print("no transaction")
            for elem in itertools.zip_longest(transactions, memberships):
                if elem[1] is not None and elem[0] is not None:
                    f.writelines(f'|{i}|{adherent.login}|{adherent.created_at}|{adherent.updated_at}|{account.name}|{elem[1].first_time}|{elem[1].duration}|{elem[0].name}|{elem[0].timestamp}|\n')
                elif elem[1] is not None:
                    f.writelines(f'|{i}|{adherent.login}|{adherent.created_at}|{adherent.updated_at}|{account.name}|{elem[1].first_time}|{elem[1].duration}|||\n')
                else:
                    f.writelines(f'||||||||{elem[0].name}|{elem[0].timestamp}|\n')


@manager.command
def reset_membership():
    s: Session = Database.get_db().get_session()
    memberships: List[Membership] = s.query(Membership).all()
    for m in memberships:
        print(m.uuid)
        s.delete(m)
    s.commit()

@manager.command
def seed():
    """Add seed data to the database."""
    s = Database.get_db().get_session()

    print("Seeding account types")
    account_types = [1,"Special"],[2,"Adherent"],[3,"Club interne"],[4,"Club externe"],[5,"Association externe"]
    for type in account_types:
        s.add(
            AccountType(
                id=type[0],
                name=type[1]
            )
        )

    print("Seeding MiNET accounts")
    accounts = [1, 1, "MiNET frais techniques", True, None, True, True],[2, 1, "MiNET frais asso", True, None, True, True]
    for account in accounts:
        s.add(
            Account(
                id=account[0],
                type=account[1],
                name=account[2],
                actif=account[3],
                adherent_id=account[4],
                compte_courant=account[5],
                pinned=account[6]
            )
        )

    print("Seeding Products")
    products = [1,"Cable 3m", 3, 3],[2,"Cable 5m", 5, 5],[3,"Adaptateur USB/Ethernet", 13.00, 13.00],[4,"Adaptateur USB-C/Ethernet", 12.00, 12.00]
    for product in products:
        s.add(
            Product(
                id=product[0],
                name=product[1],
                buying_price=product[2],
                selling_price=product[3]
            )
        )

    print("Seeding payment methods")
    payment_methods = [1,"Liquide"],[2,"Chèque"],[3,"Carte bancaire"],[4,"Virement"],[5,"Stripe"]
    for method in payment_methods:
        s.add(
            PaymentMethod(
                id=method[0],
                name=method[1]
            )
        )

    print("Seeding cashbox")
    s.add(Caisse(
        fond=0,
        coffre=0
    ))

    print("Seeding vlans")
    s.bulk_save_objects([
        Vlan(
            numero=35,
            adresses="10.42.0.0/16",
            adressesv6="",
            excluded_addr="",
            excluded_addrv6="",
        ),
        Vlan(
            numero=36,
            adresses="157.159.192.0/22",
            adressesv6="",
            excluded_addr="157.159.195.0/24",
            excluded_addrv6="",
        ),
        Vlan(
            numero=30,
            adresses="172.30.0.0/16",
            adressesv6="",
            excluded_addr="",
            excluded_addrv6="",
        ),
        Vlan(
            numero=41,
            adresses="157.159.41.0/24",
            adressesv6="",
            excluded_addr="157.159.41.1/32",
            excluded_addrv6="",
        )
    ])

    s.commit()


@manager.option('-l', '--login', help='Your login', default='dummy_user')
@manager.command
def fake(login):
    """Add dummy data to the database."""
    fake = Faker()
    s = Database.get_db().get_session()
    #switch = Switch(
    #    description="Dummy switch",
    #    ip="192.168.254.254",
    #    communaute="adh6",
    #)
    #s.add(switch)

    switch2 = Switch(
        description="Switch local",
        ip="192.168.102.219",
        communaute="adh5",
    )
    s.add(switch2)

    chambres = []
    for n in range(1, 30):
        chambre = Chambre(
            numero=n,
            description="Chambre " + str(n),
            vlan_id=3
        )
        chambres.append(chambre)
        s.add(chambre)

    #for n in range(1, 10):
    #    s.add(Port(
    #        rcom=0,
    #        numero="1/0/" + str(n),
    #        oid="1010" + str(n),
    #        switch=switch,
    #        chambre=chambres[n - 1]
    #    ))

    for n in range(1, 10):
        s.add(Port(
            rcom=0,
            numero="1/0/" + str(n),
            oid="1010" + str(n),
            switch=switch2,
            chambre=chambres[n-1]
        ))


    for n in range(10, 20):
        s.add(Port(
            rcom=0,
            numero="1/0/" + str(n),
            oid="101" + str(n),
            switch=switch2,
            chambre=chambres[n-1]
        ))


    admin = Admin(
        roles="adh6_user,adh6_admin,adh6_treso,adh6_superadmin"
    )
    s.add(admin)

    adherent = Adherent(
        nom=fake.last_name_nonbinary(),
        prenom=fake.first_name_nonbinary(),
        mail=fake.email(),
        login=login,
        password="",
        chambre=chambres[2],
        admin=admin
    )
    s.add(adherent)
    s.add(
        Account(
            type=1,
            name=adherent.nom + " " + adherent.prenom,
            actif=True,
            compte_courant=True,
            pinned=False,
            adherent=adherent
        )
    )

    for n in range(1, 4):
        s.add(Device(
            mac=fake.mac_address(),
            ip=None,
            adherent=adherent,
            ipv6=None,
            type=0
        ))
    for n in range(1, 4):
        s.add(Device(
            mac=fake.mac_address(),
            ip=None,
            adherent=adherent,
            ipv6=None,
            type=1
        ))
    s.commit()



if __name__ == '__main__':
    manager.run()
