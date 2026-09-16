"""Addresses of a mini-router, all derived from its MiNET number."""

import re
from typing import NamedTuple

IP_WIREGUARD_PREFIX = "10.31.0."
IP_VLAN31_PREFIX = "172.30.0."
MAC_ACCEPT_PREFIX = "00:00:36:00:"
MAC_DENY_PREFIX = "36:36:36:00:"

_IP_TERMS = re.compile(r"^(?:10\.31\.0\.|172\.30\.0\.)?(\d{1,3})$")
_MAC_TERMS = re.compile(r"^(?:00:00:36|36:36:36):00:0(\d):(\d\d)$")


class Addresses(NamedTuple):
    ip_wireguard: str
    ip_vlan31: str
    mac_accept: str
    mac_deny: str


def addresses_of(number: int) -> Addresses:
    # 115 -> "01:15", 98 -> "00:98"
    digits = f"{number:03d}"
    mac_suffix = f"0{digits[0]}:{digits[1:]}"
    return Addresses(
        ip_wireguard=f"{IP_WIREGUARD_PREFIX}{number}",
        ip_vlan31=f"{IP_VLAN31_PREFIX}{number}",
        mac_accept=f"{MAC_ACCEPT_PREFIX}{mac_suffix}",
        mac_deny=f"{MAC_DENY_PREFIX}{mac_suffix}",
    )


def number_from_terms(terms: str) -> int | None:
    """The number designated by a search on a full or partial IP, or on a full MAC."""
    terms = terms.strip().lower().replace("-", ":")
    if match := _IP_TERMS.match(terms):
        return int(match.group(1))
    if match := _MAC_TERMS.match(terms):
        return int(match.group(1) + match.group(2))
    return None
