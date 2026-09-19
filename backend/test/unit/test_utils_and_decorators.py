"""Tests for pure Python utility functions to increase coverage."""

from datetime import timedelta
from unittest.mock import MagicMock

from adh6.datetime_utils import utc_now_naive, utc_today
from adh6.entity import AbstractDevice, Member


def test_generated_entity_to_json_preserves_explicit_null_and_omits_unset_fields():
    device = AbstractDevice(id=42, ipv4Address=None)

    assert device.to_json() == '{"id":42,"ipv4Address":null}'


# ===========================================================================
# member_validators tests
# ===========================================================================
class TestIsMemberActive:
    def test_no_departure_date(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.permanent = False
        member.departure_date = None
        assert is_member_active(member) is False

    def test_future_departure_date(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.permanent = False
        member.departure_date = utc_today() + timedelta(days=365)
        assert is_member_active(member) is True

    def test_past_departure_date(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.permanent = False
        member.departure_date = utc_today() - timedelta(days=1)
        assert is_member_active(member) is False

    def test_departure_date_as_datetime(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.permanent = False
        member.departure_date = utc_now_naive() + timedelta(days=365)
        assert is_member_active(member) is True

    def test_past_departure_date_as_datetime(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.permanent = False
        member.departure_date = utc_now_naive() - timedelta(days=1)
        assert is_member_active(member) is False

    def test_permanent_member(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.permanent = True
        assert is_member_active(member) is True


class TestIsPasswordValid:
    def test_valid_password(self):
        from adh6.utils.validators.member_validators import is_password_valid

        assert is_password_valid("ValidPass1!") is True

    def test_too_short(self):
        from adh6.utils.validators.member_validators import is_password_valid

        assert is_password_valid("Aa1!") is False

    def test_no_uppercase(self):
        from adh6.utils.validators.member_validators import is_password_valid

        assert is_password_valid("validpass1!") is False

    def test_no_lowercase(self):
        from adh6.utils.validators.member_validators import is_password_valid

        assert is_password_valid("VALIDPASS1!") is False

    def test_no_digit(self):
        from adh6.utils.validators.member_validators import is_password_valid

        assert is_password_valid("ValidPass!") is False

    def test_no_special_char(self):
        from adh6.utils.validators.member_validators import is_password_valid

        assert is_password_valid("ValidPass1") is False

    def test_too_long(self):
        from adh6.utils.validators.member_validators import is_password_valid

        assert is_password_valid("A" * 62 + "a1!") is False  # 65 chars > 64


class TestHasMemberSubnet:
    def test_has_subnet(self):
        from adh6.utils.validators.member_validators import has_member_subnet

        member = MagicMock(spec=Member)
        member.ip = "192.168.1.1"
        member.subnet = "192.168.1.0/24"
        assert has_member_subnet(member) is True

    def test_no_ip(self):
        from adh6.utils.validators.member_validators import has_member_subnet

        member = MagicMock(spec=Member)
        member.ip = None
        member.subnet = "192.168.1.0/24"
        assert has_member_subnet(member) is False

    def test_no_subnet(self):
        from adh6.utils.validators.member_validators import has_member_subnet

        member = MagicMock(spec=Member)
        member.ip = "192.168.1.1"
        member.subnet = None
        assert has_member_subnet(member) is False
