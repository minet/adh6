# coding=utf-8
import datetime
import ipaddress

from sqlalchemy.orm.session import Session

from src.interface_adapter.sql.model.models import Device, Adherent


def get_available_ip(network, ip_taken):
    network = ipaddress.ip_network(network)
    ip_taken = set(map(lambda x: ipaddress.ip_address(x), ip_taken))
    available = filter(lambda x: x not in ip_taken, network.hosts())
    try:
        # two times "next()" because we want to skip the first address, which
        # is the gateway address
        next(available)
        ip = next(available)
    except StopIteration:
        return None

    return str(ip)


def get_all_used_ipv4(session: Session):
    query = session.query(Device)
    query = query.filter(Device.ip != "En Attente")
    return list(map(lambda x: x.ip, query.all()))


def get_all_used_ipv6(session: Session):
    query = session.query(Device)
    query = query.filter(Device.ipv6 != "En Attente")
    return list(map(lambda x: x.ipv6, query.all()))


def _get_expired_devices(session: Session):
    query = session.query(Device)
    query = query.filter(Device.ip != "En Attente")
    query = query.join(Adherent)
    query = query.filter(Adherent.date_de_depart < datetime.datetime.now())
    return list(query.all())
"""
def _free_expired_devices(session: Session):
    for dev in _get_expired_devices(session):
        dev.ip = "En Attente"
        dev.ipv6 = "En Attente"
"""