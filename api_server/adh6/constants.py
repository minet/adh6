# coding=utf-8
import enum
import ipaddress
import typing as t

DEFAULT_LIMIT = 100
DEFAULT_OFFSET = 0
LOG_DEFAULT_LIMIT = 10


class KnownAccountExpense(enum.Enum):
    TECHNICAL_EXPENSE = "MiNET frais techniques"
    ASSOCIATION_EXPENCE = "MiNET frais asso"


PUBLIC_RANGE = ipaddress.IPv4Network("157.159.192.0/22").address_exclude(ipaddress.IPv4Network("157.159.195.0/24"))

def dictionnary_subnet_public_ip_wireless() -> t.Dict[ipaddress.IPv4Address, ipaddress.IPv4Network]:
    # These are perfectly valid addresses, but we exclude them to avoid confusion
    excluded_addresses = ["157.159.192.0", "157.159.192.1", "157.159.192.255", "157.159.193.0", "157.159.193.1", "157.159.193.255", "157.159.194.0", "157.159.194.1", "157.159.194.255"]
    hosts = []
    for r in PUBLIC_RANGE:
        hosts.extend(list(r.hosts()))

    private_range = ipaddress.IPv4Network("10.42.0.0/16").subnets(new_prefix=28)

    mappings: t.Dict[ipaddress.IPv4Address, ipaddress.IPv4Network] = {}
    for subnet, ip in zip(private_range, hosts):
        if str(ip) in excluded_addresses:
            continue
        mappings[ip] = subnet

    return mappings

SUBNET_PUBLIC_ADDRESSES_WIRELESS = dictionnary_subnet_public_ip_wireless()
