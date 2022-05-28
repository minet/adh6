# coding=utf-8
# from datetime import datetime
import re
from ipaddress import (
    IPv4Address,
    IPv6Address, 
    AddressValueError
)

MAC_REGEX = re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def is_mac_address(mac_address: str) -> bool:
    """ Allowed MAC address format: DE-AD-BE-EF-01-23 """
    mac_address = str(mac_address).upper()
    return bool(MAC_REGEX.match(mac_address))


def is_ip_v4(ip_address: str) -> bool:
    """ Allowed format: 192.168.0.1 """
    try:
        IPv4Address(ip_address)
    except AddressValueError:
        return False
    return True


def is_ip_v6(ip_address: str) -> bool:
    """ Allowed format: fe80:0000:0000:0000:62eb:69ff:feec:c643 """
    try:
        IPv6Address(ip_address)
    except AddressValueError:
        return False
    return True
