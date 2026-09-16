import pytest
from adh6.mini_router.addresses import Addresses, addresses_of, number_from_terms


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (115, Addresses("10.31.0.115", "172.30.0.115", "00:00:36:00:01:15", "36:36:36:00:01:15")),
        (98, Addresses("10.31.0.98", "172.30.0.98", "00:00:36:00:00:98", "36:36:36:00:00:98")),
        (7, Addresses("10.31.0.7", "172.30.0.7", "00:00:36:00:00:07", "36:36:36:00:00:07")),
        (254, Addresses("10.31.0.254", "172.30.0.254", "00:00:36:00:02:54", "36:36:36:00:02:54")),
    ],
)
def test_addresses_of(number, expected):
    assert addresses_of(number) == expected


@pytest.mark.parametrize(
    ("terms", "expected"),
    [
        ("115", 115),
        ("10.31.0.115", 115),
        ("172.30.0.98", 98),
        ("00:00:36:00:01:15", 115),
        ("36-36-36-00-00-98", 98),
        ("94:83", None),
        ("10.30.0.115", None),
        ("dubois", None),
    ],
)
def test_number_from_terms(terms, expected):
    assert number_from_terms(terms) == expected
