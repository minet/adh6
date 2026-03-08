from datetime import datetime
from typing import Any, Literal

from fastapi import Depends, Request

from adh6.entity.abstract_port import AbstractPort
from adh6.entity.abstract_switch import AbstractSwitch
from adh6.entity.device_filter import DeviceFilter
from adh6.entity.member_filter import MemberFilter


def _extract_filter_entries(request: Request) -> dict[str, str]:
    filters: dict[str, str] = {}
    for raw_key, raw_value in request.query_params.multi_items():
        if not raw_key.startswith("filter[") or not raw_key.endswith("]"):
            continue

        key = raw_key[len("filter[") : -1]
        if key:
            filters[key] = raw_value

    return filters


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _parse_optional_datetime(value: str | None) -> datetime | None:
    if value is None or value == "":
        return None
    return datetime.fromisoformat(value)


def _build_device_filter_dependency() -> Any:
    def dependency(request: Request) -> DeviceFilter:
        raw_filters = _extract_filter_entries(request)
        payload = {
            # Only keep supported keys for device search filters.
            "terms": raw_filters.get("terms") if "terms" in raw_filters else None,
            "member": _parse_optional_int(raw_filters.get("member")),
            "connectionType": (
                raw_filters.get("connectionType")
                if "connectionType" in raw_filters
                else None
            ),
        }
        return DeviceFilter.from_dict(payload)

    return dependency


def _build_member_filter_dependency() -> Any:
    def dependency(request: Request) -> MemberFilter:
        raw_filters = _extract_filter_entries(request)
        payload = {
            # Only keep supported keys for member search filters.
            "membership": (
                raw_filters.get("membership") if "membership" in raw_filters else None
            ),
            "mailinglist": _parse_optional_int(raw_filters.get("mailinglist")),
            "since": _parse_optional_datetime(raw_filters.get("since")),
            "until": _parse_optional_datetime(raw_filters.get("until")),
            "ip": raw_filters.get("ip") if "ip" in raw_filters else None,
        }
        return MemberFilter.from_dict(payload)

    return dependency


def _build_abstract_port_filter_dependency() -> Any:
    def dependency(request: Request) -> AbstractPort:
        raw_filters = _extract_filter_entries(request)
        payload = {
            # Only keep supported keys for port search filters.
            "id": _parse_optional_int(raw_filters.get("id")),
            "portNumber": (
                raw_filters.get("portNumber") if "portNumber" in raw_filters else None
            ),
            "oid": raw_filters.get("oid") if "oid" in raw_filters else None,
            "room": _parse_optional_int(raw_filters.get("room")),
            "switchObj": _parse_optional_int(raw_filters.get("switchObj")),
        }
        return AbstractPort.from_dict(payload)

    return dependency


def _build_abstract_switch_filter_dependency() -> Any:
    def dependency(request: Request) -> AbstractSwitch:
        raw_filters = _extract_filter_entries(request)
        payload = {
            "id": _parse_optional_int(raw_filters.get("id")),
            "description": (
                raw_filters.get("description") if "description" in raw_filters else None
            ),
            "ip": raw_filters.get("ip") if "ip" in raw_filters else None,
        }
        return AbstractSwitch.from_dict(payload)

    return dependency


def DeviceFilterWrapper(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return Depends(
        dependency=_build_device_filter_dependency(),
        use_cache=use_cache,
        scope=scope,
    )


def MemberFilterWrapper(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return Depends(
        dependency=_build_member_filter_dependency(),
        use_cache=use_cache,
        scope=scope,
    )


def AbstractPortFilterWrapper(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return Depends(
        dependency=_build_abstract_port_filter_dependency(),
        use_cache=use_cache,
        scope=scope,
    )


def DeviceFilterHandler(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return DeviceFilterWrapper(use_cache=use_cache, scope=scope)


def MemberFilterHandler(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return MemberFilterWrapper(use_cache=use_cache, scope=scope)


def AbstractPortFilterHandler(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return AbstractPortFilterWrapper(use_cache=use_cache, scope=scope)


def AbstractSwitchFilterWrapper(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return Depends(
        dependency=_build_abstract_switch_filter_dependency(),
        use_cache=use_cache,
        scope=scope,
    )


def AbstractSwitchFilterHandler(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return AbstractSwitchFilterWrapper(use_cache=use_cache, scope=scope)


def AbstractPortHandler(
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Any:
    return AbstractPortFilterWrapper(use_cache=use_cache, scope=scope)


__all__ = [
    "DeviceFilterWrapper",
    "MemberFilterWrapper",
    "AbstractPortFilterWrapper",
    "AbstractSwitchFilterWrapper",
    "DeviceFilterHandler",
    "MemberFilterHandler",
    "AbstractPortFilterHandler",
    "AbstractPortHandler",
    "AbstractSwitchFilterHandler",
]
