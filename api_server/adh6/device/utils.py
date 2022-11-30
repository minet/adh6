# coding=utf-8
import string

def get_mac_variations(addr):
    addr = filter(lambda x: x in string.hexdigits, addr)
    addr = "".join(addr)
    addr = addr.lower()
    variations = []
    variations += ["{}:{}:{}:{}:{}:{}".format(*(addr[i * 2:(i + 1) * 2] for i in range(6)))]
    variations += ["{}-{}-{}-{}-{}-{}".format(*(addr[i * 2:(i + 1) * 2] for i in range(6)))]
    variations += ["{}.{}.{}".format(*(addr[i*4:(i + 1)*4] for i in range(3)))]
    variations += list(map(lambda x: x.upper(), variations))
    return variations

# coding=utf-8
# from datetime import datetime
import re

MAC_REGEX = re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def is_mac_address(mac_address: str) -> bool:
    """ Allowed MAC address format: DE-AD-BE-EF-01-23 """
    mac_address = str(mac_address).upper()
    return bool(MAC_REGEX.match(mac_address))
