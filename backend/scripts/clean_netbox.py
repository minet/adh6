import logging
import os

import pynetbox
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

NETBOX_URL = os.getenv("NETBOX_URL")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")
NETBOX_TAG_SLUG = os.getenv("NETBOX_TAG_SLUG")

netbox = pynetbox.api(
    NETBOX_URL,
    token=NETBOX_TOKEN,
)

to_delete = netbox.ipam.ip_addresses.filter(tag=NETBOX_TAG_SLUG)
if to_delete:
    input(f"About to delete {len(to_delete)} IP addresses tagged with '{NETBOX_TAG_SLUG}'. Press Enter to continue...")

for ip_address in to_delete:
    print(f"Deleting IP {ip_address.address} (ID: {ip_address.id})")
    ip_address.delete()

to_delete = netbox.ipam.prefixes.filter(tag=NETBOX_TAG_SLUG)
if to_delete:
    input(f"About to delete {len(to_delete)} prefixes tagged with '{NETBOX_TAG_SLUG}'. Press Enter to continue...")

for prefix in to_delete:
    print(f"Deleting prefix {prefix.prefix} (ID: {prefix.id})")
    prefix.delete()
