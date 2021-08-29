from threading import active_count
from flask_sqlalchemy import SQLAlchemy

from common import init
from flask_script import Manager
from flask_migrate import MigrateCommand
from faker import Faker

from src.interface_adapter.sql.model.database import Database
from src.interface_adapter.sql.model.models import Adherent, AccountType, PaymentMethod, Vlan, Switch, Port, Chambre, \
    Admin, Caisse, Account, Device, Product

application, migrate = init(testing=False, managing=True)

manager = Manager(application.app)
manager.add_command('db', MigrateCommand)

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
    switch = Switch(
        description="Dummy switch",
        ip="192.168.254.254",
        communaute="adh6",
    )
    s.add(switch)

    chambres = []
    for n in range(1, 10):
        chambre = Chambre(
            numero=n,
            description="Chambre " + str(n),
            vlan_id=3
        )
        chambres.append(chambre)
        s.add(chambre)

    for n in range(1, 10):
        s.add(Port(
            rcom=0,
            numero="1/0/" + str(n),
            oid="1010" + str(n),
            switch=switch,
            chambre=chambres[n - 1]
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
