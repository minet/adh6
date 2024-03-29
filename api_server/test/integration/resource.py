from logging import LogRecord
import uuid

from adh6.storage.sql.models import Modification

from test import TESTING_CLIENT_TOKEN, SAMPLE_CLIENT_TOKEN

base_url = "api"
api_key_admin = str(uuid.uuid4())
device_cazal = {
    'mac': 'FF-FF-FF-FF-FF-FF',
    'ipAddress': '127.0.0.1',
    'ipv6Address': 'fe80::0',
    'connectionType': 'wired',
    'username': 'cazal_k'
}

device_bonnet = {
    'mac': '00-00-00-00-00-00',
    'ipAddress': '127.0.0.2',
    'ipv6Address': 'fe80::1',
    'connectionType': 'wireless',
    'username': 'bonnet_n'
}

INVALID_IPv6 = [
    "",  # Empty string
    "randomString",  # Some random data
    "::::",  # Only delimiters
    "2001:660:3203:i08::a79",  # wrong character
    42,  # Wrong type
]

INVALID_IP = [
    "",  # Empty string
    "randomString",  # Some random data
    "192.168",  # Unfinished string
    "....",  # Only delimiters
    "200.256.200.200",  # Number > 255
    "-1.200.200.200",  # Number < 0
    "192.168.0.0/24",  # Address with mask
    "192.168.0.0-10",  # Address range
    42,  # Wrong type
]

INVALID_MAC = [
    "",  # Empty string
    "AA-AA-AA-",  # Unfinished MAC address
    "AA-AA-AA-AA-AA-AA-BB",  # MAC address too long
    "randomString",  # Random data
    "-----",  # Only delimiters
    "12-34-56-78-9A-BG",  # Non hexa byte (BG)
    42,  # Wrong type
]

TEST_HEADERS = {"Authorization": f"Bearer {TESTING_CLIENT_TOKEN}"}
TEST_HEADERS_SAMPLE = {"Authorization": f"Bearer {SAMPLE_CLIENT_TOKEN}"}
TEST_HEADERS_API_KEY_USER = {"X-API-KEY": str(uuid.uuid4())}
TEST_HEADERS_API_KEY_ADMIN = {"X-API-KEY": str(uuid.uuid4())}
TEST_HEADERS_API_KEY = TEST_HEADERS_API_KEY_ADMIN
TEST_HEADERS_API_KEY_TRESO = {"X-API-KEY": str(uuid.uuid4())}
TEST_HEADERS_API_KEY_NETWORK = {"X-API-KEY": str(uuid.uuid4())}
TEST_HEADERS_API_KEY_NETWORK_DEV = {"X-API-KEY": str(uuid.uuid4())}
TEST_HEADERS_API_KEY_NETWORK_PROD = {"X-API-KEY": str(uuid.uuid4())}
TEST_HEADERS_API_KEY_NETWORK_HOSTING = {"X-API-KEY": str(uuid.uuid4())}

INVALID_TRANSACTION_VALUE = [
    "",
    "-1",
    "-1120192834923949",
    "0.123",
    "0,123",
    "test"
]

def assert_modification_was_created(s):
    q = s.query(Modification)
    assert q.count() >= 1


def _records_contains_fields(record: LogRecord, fields: dict):
    if not fields:
        return True

    try:
        record.extra
    except AttributeError:
        return False

    for k,v in fields.items():
        if k not in record.extra:
            return False

        if record.extra[k] != v:
            return False

    return True


def logs_contains(caplog, log_msg, **extra_fields):
    if any(log_msg in m for m in caplog.messages) is False:
        return False

    return any(_records_contains_fields(r, extra_fields) for r in caplog.records)
