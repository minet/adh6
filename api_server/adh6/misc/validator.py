# coding=utf-8
# from datetime import datetime
import re

MAC_REGEX = re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def is_mac_address(mac_address: str) -> bool:
    """ Allowed MAC address format: DE-AD-BE-EF-01-23 """
    mac_address = str(mac_address).upper()
    return bool(MAC_REGEX.match(mac_address))
