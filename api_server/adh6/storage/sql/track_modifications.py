# coding=utf-8
"""
Track modification on SQLAlchemy objects.
"""
from contextlib import contextmanager
from datetime import datetime

from adh6.storage.sql.models import Modification
from adh6.storage.sql.trackable import RubyHashTrackable


@contextmanager
def track_modifications(session, obj: RubyHashTrackable):
    """
    Track the modifications of the specified entry and create a new entry in the modification table containing the diff.

    Object must inherit from RubyHashTrackable.
    """
    snap_before = obj.take_snapshot()  # Save the state of the object before actually modifying it.
    try:
        yield
    finally:
        diff = _get_diff(session, snap_before, obj)
        if diff is None:
            return  # No modification.

        now = datetime.now()
        from adh6.context import get_user
        user = get_user()
        member = obj.get_related_member()

        m = Modification(
            adherent_id=member,
            action=diff,
            created_at=now,
            updated_at=now,
            utilisateur_id=user,
        )
        session.add(m)


def _get_diff(session, snap_before, obj):
    if obj in session.new:
        return obj.serialize_snapshot_diff(None, obj.take_snapshot())

    if obj in session.deleted:
        return obj.serialize_snapshot_diff(snap_before, None)

    # Not deleted nor created, flush it to the database (not commit!) and compare the current state with the old state.
    #
    # Note: We need to flush here to put the object in a consistent state. For instance if we modify Member.room the
    # foreign key Member.room_id will not be updated until we flush it.
    #
    # Note2: flushing is not commit! The transaction can still be roll-backed if something goes wrong.
    session.flush()
    if snap_before != obj.take_snapshot():
        return obj.serialize_snapshot_diff(snap_before, obj.take_snapshot())
