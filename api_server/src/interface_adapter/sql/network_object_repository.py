# coding=utf-8
"""
Implements everything related to actions on the SQL database.
This deals with all the network objects (except the member'session devices).
"""
from datetime import datetime
from typing import List, Tuple

from sqlalchemy.orm.session import Session

from sqlalchemy import or_

from src.constants import CTX_SQL_SESSION, DEFAULT_LIMIT, DEFAULT_OFFSET
from src.entity.abstract_port import AbstractPort
from src.entity.abstract_switch import AbstractSwitch
from src.exceptions import SwitchNotFoundError, PortNotFoundError, RoomNotFoundError
from src.interface_adapter.sql.model.models import Chambre
from src.interface_adapter.sql.model.models import Port as PortSQL
from src.interface_adapter.sql.model.models import Switch as SwitchSQL
from src.use_case.interface.port_repository import PortRepository
from src.use_case.interface.switch_repository import SwitchRepository
from src.util.context import log_extra
from src.util.log import LOG


class NetworkObjectSQLRepository(PortRepository, SwitchRepository):

    def search_switches_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, switch_id: str = None,
                           terms: str = None) -> Tuple[List[AbstractSwitch], int]:
        """
        Search for a switch.
        """
        LOG.debug("sql_network_object_repository_search_switch_by",
                  extra=log_extra(ctx, switch_id=switch_id, terms=terms))

        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(SwitchSQL)

        if switch_id is not None:
            query = query.filter(SwitchSQL.id == switch_id)

        if terms is not None:
            query = query.filter(or_(
                SwitchSQL.description.contains(terms),
                SwitchSQL.ip.contains(terms),
            ))

        count = query.count()
        query = query.order_by(SwitchSQL.description.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        result = query.all()

        result = map(_map_switch_sql_to_abstract_entity, result)
        result = list(result)
        return result, count

    def create_switch(self, ctx, ip_v4=None, description=None, community=None) -> str:
        # Please do not log community...
        LOG.debug("sql_network_object_repository_create_switch",
                  extra=log_extra(ctx, ip_v4=ip_v4, description=description))

        session: Session = ctx.get(CTX_SQL_SESSION)
        switch = SwitchSQL(
            ip=ip_v4,
            description=description,
            communaute=community,
        )
        session.add(switch)
        session.flush()

        return str(switch.id)

    def update_switch(self, ctx, switch_id, ip_v4=None, description=None, community=None) -> None:
        # Please do not log community...
        LOG.debug("sql_network_object_repository_update_switch",
                  extra=log_extra(ctx, switch_id=switch_id, ip_v4=ip_v4, description=description))

        session: Session = ctx.get(CTX_SQL_SESSION)
        result: SwitchSQL = session.query(SwitchSQL).filter(SwitchSQL.id == int(switch_id)).one_or_none()
        if not result:
            raise SwitchNotFoundError(switch_id)

        result.communaute = community
        result.ip = ip_v4
        result.description = description

    def delete_switch(self, ctx, switch_id: str) -> None:
        LOG.debug("sql_network_object_repository_delete_switch", extra=log_extra(ctx, switch_id=switch_id))

        session: Session = ctx.get(CTX_SQL_SESSION)
        result: SwitchSQL = session.query(SwitchSQL).filter(SwitchSQL.id == int(switch_id)).one_or_none()
        if not result:
            raise SwitchNotFoundError(switch_id)

        session.delete(result)

    def search_port_by(self, ctx, limit=DEFAULT_LIMIT, offset=DEFAULT_OFFSET, port_id: str = None,
                       switch_id: str = None,
                       room_number: str = None, terms: str = None) -> Tuple[List[AbstractPort], int]:
        """
        Search for a port.
        :return: the ports and the number of matches in the DB.
        """
        LOG.debug("sql_network_object_repository_search_port_by",
                  extra=log_extra(ctx, port_id=port_id, switch_id=switch_id, room_number=room_number, terms=terms))

        session: Session = ctx.get(CTX_SQL_SESSION)

        query = session.query(PortSQL)

        if port_id:
            query = query.filter(PortSQL.id == port_id)

        if switch_id:
            query = query.join(SwitchSQL)
            query = query.filter(SwitchSQL.id == switch_id)

        if room_number:
            query = query.join(Chambre)
            query = query.filter(Chambre.numero == room_number)

        if terms:
            query = query.filter(or_(
                PortSQL.numero.contains(terms),
                PortSQL.oid.contains(terms),
            ))

        count = query.count()
        query = query.order_by(PortSQL.switch_id.asc(), PortSQL.numero.asc())
        query = query.offset(offset)
        query = query.limit(limit)
        result = query.all()

        result = map(_map_port_sql_to_abstract_entity, result)
        result = list(result)
        return result, count

    def create_port(self, ctx, rcom=None, port_number=None, oid=None, switch_id=None, room_number=None) -> str:
        """
        Create a port in the database
        :return the newly created port ID

        :raise InvalidRoomNumber
        :raise InvalidSwitchID
        """
        LOG.debug("sql_network_object_repository_create_port",
                  extra=log_extra(ctx, rcom=rcom, port_number=port_number, oid=oid, switch_id=switch_id,
                                  room_number=room_number))

        session: Session = ctx.get(CTX_SQL_SESSION)
        now = datetime.now()

        room = session.query(Chambre).filter(Chambre.numero == room_number).one_or_none()
        if room is None:
            raise RoomNotFoundError(room_number)

        switch = session.query(SwitchSQL).filter(SwitchSQL.id == switch_id).one_or_none()
        if switch is None:
            raise SwitchNotFoundError(switch_id)

        port = PortSQL(
            rcom=rcom,
            numero=port_number,
            oid=oid,
            switch=switch,
            chambre=room,
            created_at=now,
            updated_at=now,
        )
        session.add(port)
        session.flush()

        return str(port.id)

    def update_port(self, ctx, port_id=None, rcom=None, port_number=None, oid=None, switch_id=None,
                    room_number=None) -> None:
        """
        Update a port in the database
        :return the newly created port ID

        :raise PortNotFound
        :raise InvalidRoomNumber
        :raise InvalidSwitchID
        """
        LOG.debug("sql_network_object_repository_udpate_port",
                  extra=log_extra(ctx, port_id=port_id, rcom=rcom, port_number=port_number, oid=oid,
                                  switch_id=switch_id, room_number=room_number))

        session: Session = ctx.get(CTX_SQL_SESSION)
        now = datetime.now()

        port = session.query(PortSQL).filter(PortSQL.id == int(port_id)).one_or_none()
        if port is None:
            raise PortNotFoundError(port_id)

        room = session.query(Chambre).filter(Chambre.numero == room_number).one_or_none()
        if room is None:
            raise RoomNotFoundError(room_number)

        switch = session.query(SwitchSQL).filter(SwitchSQL.id == switch_id).one_or_none()
        if switch is None:
            raise SwitchNotFoundError(switch_id)

        port.rcom = rcom
        port.numero = port_number
        port.oid = oid
        port.switch = switch
        port.chambre = room
        port.updated_at = now

    def delete_port(self, ctx, port_id: str) -> None:
        """
        Delete port

        :raise PortNotFound
        """
        session: Session = ctx.get(CTX_SQL_SESSION)
        port = session.query(PortSQL).filter(PortSQL.id == port_id).one_or_none()
        if port is None:
            raise PortNotFoundError(port_id)

        session.delete(port)


def _map_switch_sql_to_abstract_entity(r: SwitchSQL) -> AbstractSwitch:
    return AbstractSwitch(
        id=str(r.id),
        description=r.description,
        ip=r.ip,
    )


def _map_port_sql_to_abstract_entity(r: PortSQL) -> AbstractPort:
    return AbstractPort(
        id=str(r.id),
        port_number=r.numero,
        room=r.chambre.id,
        switch_obj=r.switch.id,
        oid=r.oid,
    )
