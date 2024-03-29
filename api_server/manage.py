import click
from flask import Flask
import uuid
from datetime import date, datetime
from typing import List
from sqlalchemy.orm import Session
from adh6.authentication import AuthenticationMethod
from adh6.server import init
from faker import Faker

import ipaddress
from adh6.constants import MembershipDuration, MembershipStatus
from adh6.authentication import Roles
from adh6.authentication.storage.models import ApiKey, AuthenticationRoleMapping
from adh6.storage import db
from adh6.storage.sql.models import Adhesion, Modification, Routeur
from adh6.member.storage.models import Adherent, Membership, NotificationTemplate
from adh6.treasury.storage.models import AccountType, PaymentMethod, Transaction, Caisse, Account, Product
from adh6.device.storage.models import Device
from adh6.network.storage.models import Switch, Port
from adh6.subnet.storage.models import Vlan
from adh6.room.storage.models import Chambre

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


@manager.cli.command("api_key")
@click.argument("login")
def api_key(login: str = "dev-api-key"):
    """Add seed data to the database."""
    session: Session = db.session

    print("Generate api key")
    api_key = (str(uuid.uuid4()), login, Roles.ADMIN_READ.value)
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
    payment_methods = [1,"Liquide"],[2,"Chèque"],[3,"Carte bancaire"],[4,"Virement"],[5,"Stripe"],[6,"Aucun"]
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
    print("Seeding role mapping for oidc")
    session.bulk_save_objects(
        [
            AuthenticationRoleMapping(
                identifier="adh6_admin",
                role=i,
                authentication=AuthenticationMethod.OIDC
            ) for i in [Roles.ADMIN_READ, Roles.ADMIN_WRITE, Roles.NETWORK_READ, Roles.NETWORK_WRITE, Roles.ADMIN_PROD]
        ] 
    )

    session.bulk_save_objects(
        [
            AuthenticationRoleMapping(
                identifier="adh6_treso",
                role=i,
                authentication=AuthenticationMethod.OIDC
            ) for i in [Roles.TRESO_READ, Roles.TRESO_WRITE]
        ] 
    )

    print("Seeding email template")
    session.add(
        NotificationTemplate(
            title="Nouvelle cotisation / New subscription",
            template="""
-- ENGLISH VERSION BELOW --

Bonjour/Bonsoir,

Ta cotisation de {{ subscription_duration }} mois a bien été prise en compte. Elle expirera le {{ subscription_end.strftime('%d/%m/%Y') }}.

Pour configurer tes appareils, nous t'invitons à te rendre sur le site https://minet.net/fr/tutoriels.html qui t'explique comment configurer tes appareils. En cas de problème, tu peux nous écrire sur https://tickets.minet.net, et nous t'aiderons à régler tes problèmes, ou bien passer au local associatif dans le foyer, aux horaires de permanence (du lundi au vendredi de 18h à 19h30).

Cordialement,
L'équipe MiNET.

----

Hello/Good evening,

Your subscription of {{ subscription_duration }} months has been taken into account. It will expire on {{ subscription_end.strftime('%m-%d-%Y') }}.

To configure your devices, we invite you to visit https://minet.net/en/tutoriels.html which explains how to configure your devices. In case of problem, you can write to us on https://tickets.minet.net/, and we will help you to solve your problems, or come to the association's office in the foyer, during office hours (Monday to Friday from 6pm to 7:30pm).

Best regard,
MiNET Team.
        """
        )
    )
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
        commentaires=fake.text(max_nb_chars=255),
        datesignedminet=now,
        date_de_depart=now + dt.timedelta(days=365),
        subnet="10.0.42.0/28",
        ip="157.159.192.2"
    )

    session.add(adherent)
    session.flush()

    account = Account(
        type=2,
        name=adherent.nom + " " + adherent.prenom,
        actif=True,
        compte_courant=False,
        pinned=False,
        adherent_id=adherent.id
    )

    session.add(account)
    session.flush()

    membership = Membership(
        uuid=str(uuid.uuid4),
        account_id=account.id,
        adherent_id=adherent.id,
        payment_method_id=3,
        has_room=True,
        first_time=True,
        products="",
        update_at=datetime.now(),
        create_at=datetime.now(),
        status=MembershipStatus.PENDING_PAYMENT_VALIDATION.value,
        duration=MembershipDuration.ONE_YEAR.value
    )

    session.add(membership)
    session.flush()

    """
    session.add(Transaction(
        value=9,
        timestamp=now,
        src=account.id,
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
        src=account.id,
        dst=1,
        name="Internet - 1 an",
        attachments="",
        type=3,
        author_id=1,
        pending_validation=False,
    ))
    """
    
    for _ in range(1, 4):
        session.add(Device(
            mac=fake.mac_address(),
            ip=None,
            adherent_id=adherent.id,
            ipv6=None,
            type=0
        ))
    for _ in range(1, 4):
        session.add(Device(
            mac=fake.mac_address(),
            ip=None,
            adherent_id=adherent.id,
            ipv6=None,
            type=1
        ))
    session.commit()



if __name__ == '__main__':
    application.run()
