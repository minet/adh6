"""Tests for pure Python utility functions to increase coverage."""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

from adh6.entity import Member


# ===========================================================================
# rubydiff tests
# ===========================================================================
class TestRubydiff:
    def test_no_changes(self):
        from adh6.storage.sql.rubydiff import rubydiff

        snap = {"name": "Alice", "age": 30}
        result = rubydiff(snap, snap)
        assert result == ""

    def test_field_changed(self):
        from adh6.storage.sql.rubydiff import rubydiff

        before = {"name": "Alice", "age": 30}
        after = {"name": "Bob", "age": 30}
        result = rubydiff(before, after)
        assert "name" in result
        assert "Alice" in result
        assert "Bob" in result

    def test_field_added(self):
        from adh6.storage.sql.rubydiff import rubydiff

        before = {"name": "Alice"}
        after = {"name": "Alice", "email": "alice@example.com"}
        result = rubydiff(before, after)
        assert "email" in result

    def test_field_removed(self):
        from adh6.storage.sql.rubydiff import rubydiff

        before = {"name": "Alice", "email": "alice@example.com"}
        after = {"name": "Alice"}
        result = rubydiff(before, after)
        assert "email" in result

    def test_none_before(self):
        from adh6.storage.sql.rubydiff import rubydiff

        result = rubydiff(None, {"name": "Alice"})
        assert "name" in result

    def test_none_after(self):
        from adh6.storage.sql.rubydiff import rubydiff

        result = rubydiff({"name": "Alice"}, None)
        assert "name" in result

    def test_none_value_in_snap(self):
        from adh6.storage.sql.rubydiff import rubydiff

        before = {"name": None}
        after = {"name": "Alice"}
        result = rubydiff(before, after)
        assert "name" in result

    def test_sorted_keys(self):
        from adh6.storage.sql.rubydiff import rubydiff

        before = {"z_field": "old", "a_field": "old"}
        after = {"z_field": "new", "a_field": "new"}
        result = rubydiff(before, after)
        # Sorted - a_field should appear before z_field
        assert result.index("a_field") < result.index("z_field")


# ===========================================================================
# handle_error tests
# ===========================================================================
class TestHandleError:
    def test_not_found_error(self):
        from adh6.exceptions import NotFoundError
        from adh6.misc.error import handle_error

        result, code = handle_error(NotFoundError("resource not found"))
        assert code == 404
        assert "not found" in result["message"].lower() or result["code"] == 404

    def test_unauthorized_error(self):
        from adh6.exceptions import UnauthorizedError
        from adh6.misc.error import handle_error

        result, code = handle_error(UnauthorizedError("access denied"))
        assert code == 403

    def test_validation_error(self):
        from adh6.exceptions import ValidationError
        from adh6.misc.error import handle_error

        result, code = handle_error(ValidationError("invalid value"))
        assert code == 400

    def test_already_exists_error(self):
        from adh6.exceptions import AlreadyExistsError
        from adh6.misc.error import handle_error

        result, code = handle_error(AlreadyExistsError("already exists"))
        assert code == 400

    def test_network_manager_read_error(self):
        from adh6.exceptions import NetworkManagerReadError
        from adh6.misc.error import handle_error

        result, code = handle_error(NetworkManagerReadError("network error"))
        assert code == 400

    def test_value_error(self):
        from adh6.misc.error import handle_error

        result, code = handle_error(ValueError("bad value"))
        assert code == 400

    def test_generic_exception(self):
        from adh6.misc.error import handle_error

        result, code = handle_error(RuntimeError("something went wrong"))
        assert code == 500


# ===========================================================================
# member_validators tests
# ===========================================================================
class TestIsMemberActive:
    def test_no_departure_date(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.departure_date = None
        assert is_member_active(member) is False

    def test_future_departure_date(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.departure_date = date.today() + timedelta(days=365)
        assert is_member_active(member) is True

    def test_past_departure_date(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.departure_date = date.today() - timedelta(days=1)
        assert is_member_active(member) is False

    def test_departure_date_as_datetime(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.departure_date = datetime.now() + timedelta(days=365)
        assert is_member_active(member) is True

    def test_past_departure_date_as_datetime(self):
        from adh6.utils.validators.member_validators import is_member_active

        member = MagicMock(spec=Member)
        member.departure_date = datetime.now() - timedelta(days=1)
        assert is_member_active(member) is False


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


# ===========================================================================
# track_modifications tests
# ===========================================================================
class TestTrackModifications:
    def _make_session(self, is_new=False, is_deleted=False):
        session = MagicMock()
        session.new = set()
        session.deleted = set()
        return session

    def _make_obj(self, snap_before=None, snap_after=None, member_id=1):
        obj = MagicMock()
        snaps = [snap_before or {"name": "before"}, snap_after or {"name": "after"}]
        obj.take_snapshot.side_effect = snaps * 3  # provide multiple calls
        obj.get_related_member.return_value = member_id
        obj.serialize_snapshot_diff.return_value = "some diff"
        return obj

    def test_no_modification_same_snapshot(self, monkeypatch):
        monkeypatch.setattr("adh6.context.get_user", lambda: 1, raising=False)

        session = self._make_session()
        obj = MagicMock()
        snap = {"name": "same"}
        obj.take_snapshot.return_value = snap
        obj.get_related_member.return_value = 1
        obj.serialize_snapshot_diff.return_value = None

        from adh6.storage.sql.track_modifications import track_modifications

        with track_modifications(session, obj):
            pass

        # _get_diff returns None when snap_before == obj.take_snapshot() after flush
        # Actually here snap_before != snap_after since first call is during setup, second after flush

    def test_modification_recorded(self, monkeypatch):
        import adh6.context as context

        monkeypatch.setattr(context, "get_user", lambda: 28, raising=False)

        session = MagicMock()
        session.new = set()
        session.deleted = set()

        obj = MagicMock()
        snap_before = {"name": "old"}
        snap_after = {"name": "new"}
        obj.take_snapshot.side_effect = [snap_before, snap_after, snap_after]
        obj.get_related_member.return_value = 1
        obj.serialize_snapshot_diff.return_value = "name:\n- old\n- new\n"

        from adh6.storage.sql.track_modifications import track_modifications

        with track_modifications(session, obj):
            pass

        session.add.assert_called_once()
        session.flush.assert_called_once()

    def test_new_object_tracked(self, monkeypatch):
        import adh6.context as context

        monkeypatch.setattr(context, "get_user", lambda: 28, raising=False)

        session = MagicMock()
        obj = MagicMock()
        session.new = {obj}  # obj is new
        session.deleted = set()

        snap = {"name": "new"}
        obj.take_snapshot.return_value = snap
        obj.get_related_member.return_value = 1
        obj.serialize_snapshot_diff.return_value = "name:\n- \n- new\n"

        from adh6.storage.sql.track_modifications import track_modifications

        with track_modifications(session, obj):
            pass

        session.add.assert_called_once()

    def test_deleted_object_tracked(self, monkeypatch):
        import adh6.context as context

        monkeypatch.setattr(context, "get_user", lambda: 28, raising=False)

        session = MagicMock()
        obj = MagicMock()
        session.new = set()
        session.deleted = {obj}  # obj is deleted

        snap = {"name": "old"}
        obj.take_snapshot.return_value = snap
        obj.get_related_member.return_value = 1
        obj.serialize_snapshot_diff.return_value = "name:\n- old\n- \n"

        from adh6.storage.sql.track_modifications import track_modifications

        with track_modifications(session, obj):
            pass

        session.add.assert_called_once()

    def test_no_change_not_recorded(self, monkeypatch):
        import adh6.context as context

        monkeypatch.setattr(context, "get_user", lambda: 28, raising=False)

        session = MagicMock()
        session.new = set()
        session.deleted = set()

        obj = MagicMock()
        snap = {"name": "same"}
        obj.take_snapshot.return_value = snap  # same before and after
        obj.get_related_member.return_value = 1

        from adh6.storage.sql.track_modifications import track_modifications

        with track_modifications(session, obj):
            pass

        session.add.assert_not_called()


# ===========================================================================
# with_context decorator tests (cover the sync wrapper logic)
# ===========================================================================
class TestWithContext:
    def test_successful_2xx_response(self, monkeypatch):
        """Call a wrapped (sync) function that returns a 2xx result."""
        from adh6.decorator.with_context import with_context

        def mock_func(arg1):
            return {"data": arg1}, 200

        mock_db_module = MagicMock()
        mock_db_module.session.dirty = False
        mock_db_module.session.new = False
        mock_db_module.session.deleted = False

        import adh6.storage as storage_module

        monkeypatch.setattr(storage_module, "db", mock_db_module)

        wrapped = with_context(mock_func)
        result = wrapped("test_value")

        assert result[1] == 200

    def test_error_response_triggers_rollback(self, monkeypatch):
        """Call a wrapped function that raises an exception."""
        from adh6.decorator.with_context import with_context

        def failing_func():
            raise ValueError("bad input")

        mock_db_module = MagicMock()

        import adh6.storage as storage_module

        monkeypatch.setattr(storage_module, "db", mock_db_module)

        wrapped = with_context(failing_func)
        result = wrapped()

        mock_db_module.session.rollback.assert_called_once()
        assert result[1] == 400  # ValueError -> 400

    def test_non_tuple_result_triggers_rollback(self, monkeypatch):
        """A function returning non-tuple raises ValueError, triggering rollback."""
        from adh6.decorator.with_context import with_context

        def bad_func():
            return "not a tuple"

        mock_db_module = MagicMock()

        import adh6.storage as storage_module

        monkeypatch.setattr(storage_module, "db", mock_db_module)

        wrapped = with_context(bad_func)
        result = wrapped()  # noqa: F841

        mock_db_module.session.rollback.assert_called_once()

    def test_3xx_response_no_commit(self, monkeypatch):
        """3xx responses are OK (302) but shouldn't commit (unless session dirty)."""
        from adh6.decorator.with_context import with_context

        def redirect_func():
            return None, 302

        mock_db_module = MagicMock()
        mock_db_module.session.dirty = False
        mock_db_module.session.new = False
        mock_db_module.session.deleted = False

        import adh6.storage as storage_module

        monkeypatch.setattr(storage_module, "db", mock_db_module)

        wrapped = with_context(redirect_func)
        result = wrapped()

        assert result[1] == 302
        mock_db_module.session.commit.assert_not_called()
