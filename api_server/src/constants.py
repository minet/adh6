# coding=utf-8
import enum
import ipaddress
from typing import Dict

CTX_SQL_SESSION = 'sql_session'
CTX_ADMIN = 'admin'
CTX_TESTING = 'testing'
CTX_REQUEST_ID = 'request_uuid'
CTX_REQUEST_URL = 'url'
CTX_ROLES = 'roles'

DEFAULT_LIMIT = 100
DEFAULT_OFFSET = 0
LOG_DEFAULT_LIMIT = 10

PRICES = {
    1: 9,
    2: 18,
    3: 27,
    4: 36,
    5: 45,
    12: 50,
}

DURATION_STRING = {
    1: '1 mois',
    2: '2 mois',
    3: '3 mois',
    4: '4 mois',
    5: '5 mois',
    6: '6 mois',
    12: '1 an',
}

class MembershipStatus(enum.Enum):
    INITIAL = "INITIAL"
    PENDING_RULES = "PENDING_RULES"
    PENDING_PAYMENT_INITIAL = "PENDING_PAYMENT_INITIAL"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PENDING_PAYMENT_VALIDATION = "PENDING_PAYMENT_VALIDATION"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"


class MembershipDuration(enum.IntEnum):
    NONE = 0
    ONE_MONTH = 1
    TWO_MONTH = 2
    THREE_MONTH = 3
    FOUR_MONTH = 4
    FIVE_MONTH = 5
    SIX_MONTH = 6
    ONE_YEAR = 12

PUBLIC_RANGE = ipaddress.IPv4Network("157.159.192.0/22").address_exclude(ipaddress.IPv4Network("157.159.195.0/24"))

def dictionnary_subnet_public_ip_wireless() -> Dict[ipaddress.IPv4Address, ipaddress.IPv4Network]:
    # These are perfectly valid addresses, but we exclude them to avoid confusion
    excluded_addresses = ["157.159.192.0", "157.159.192.1", "157.159.192.255", "157.159.193.0", "157.159.193.1", "157.159.193.255", "157.159.194.0", "157.159.194.1", "157.159.194.255"]
    hosts = []
    for r in PUBLIC_RANGE:
        hosts.extend(list(r.hosts()))

    private_range = ipaddress.IPv4Network("10.42.0.0/16").subnets(new_prefix=28)

    mappings: Dict[ipaddress.IPv4Address, ipaddress.IPv4Network] = {}
    for subnet, ip in zip(private_range, hosts):
        if str(ip) in excluded_addresses:
            continue
        mappings[ip] = subnet

    return mappings

SUBNET_PUBLIC_ADDRESSES_WIRELESS = dictionnary_subnet_public_ip_wireless()
