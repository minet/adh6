"""Client for the Kea DHCPv4 control API, restricted to the host_cmds reservation commands.

Kea answers over HTTPS with basic authentication. Every answer is a JSON list holding one map
with "result" (0 success, 3 nothing found or nothing deleted, anything else an error), "text"
and sometimes "arguments". Requests need `Content-Type: application/json`, and MAC addresses
must be written aa:bb:cc:dd:ee:ff.

The servers listed in the configuration all read the same reservation database, so a command
can go to any of them: the client tries them in order and sticks to the first one that answers.
"""

from __future__ import annotations

import logging
import ssl
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self, cast

import httpx

from adh6.config.configuration import settings

logger = logging.getLogger(__name__)

KEA_SUCCESS = 0
KEA_EMPTY = 3
HTTP_OK = 200
PAGE_SIZE = 1000


class KeaError(RuntimeError):
    """Kea refused a command or returned an answer that cannot be read."""


class KeaUnavailableError(KeaError):
    """No Kea server answered."""


@dataclass(frozen=True)
class KeaReservation:
    subnet_id: int
    mac: str
    ip: str


@dataclass(frozen=True)
class KeaConfig:
    urls: tuple[str, ...]
    user: str
    password: str
    ca_file: str | None = None
    timeout_seconds: float = 5


@dataclass
class KeaClient:
    """Use as an async context manager: one HTTP connection pool per batch of commands."""

    config: KeaConfig
    transport: httpx.AsyncBaseTransport | None = None
    _client: httpx.AsyncClient | None = field(default=None, init=False, repr=False)
    _preferred: int = field(default=0, init=False, repr=False)

    async def __aenter__(self) -> Self:
        verify: ssl.SSLContext | bool = True
        if self.config.ca_file:
            verify = ssl.create_default_context(cafile=self.config.ca_file)
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout_seconds),
            verify=verify,
            auth=httpx.BasicAuth(self.config.user, self.config.password),
            transport=self.transport,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def command(self, command: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Send one command and return Kea's answer map. Raise KeaError unless result is 0 or 3."""
        if self._client is None:
            raise RuntimeError("KeaClient must be used as an async context manager")
        if not self.config.urls:
            raise KeaUnavailableError("No Kea API URL configured")

        body = {"command": command, "arguments": arguments}
        count = len(self.config.urls)
        last_error: Exception | None = None
        for attempt in range(count):
            index = (self._preferred + attempt) % count
            url = self.config.urls[index]
            try:
                response = await self._client.post(url, json=body)
            except httpx.TransportError as error:
                logger.warning("kea_api_unreachable url=%s error=%s", url, error)
                last_error = error
                continue
            if response.status_code >= 500:
                logger.warning("kea_api_server_error url=%s status=%s", url, response.status_code)
                last_error = KeaError(f"HTTP {response.status_code}")
                continue
            self._preferred = index
            return _parse_answer(command, response)
        raise KeaUnavailableError("No Kea server answered") from last_error

    async def reservations_for_mac(self, mac: str) -> list[KeaReservation]:
        answer = await self.command(
            "reservation-get-by-id",
            {"identifier-type": "hw-address", "identifier": mac, "operation-target": "database"},
        )
        return _parse_hosts(answer)

    async def all_reservations(self) -> list[KeaReservation]:
        reservations: list[KeaReservation] = []
        arguments: dict[str, Any] = {"limit": PAGE_SIZE}
        while True:
            answer = await self.command("reservation-get-page", arguments)
            page = _parse_hosts(answer)
            if not page:
                return reservations
            reservations.extend(page)
            next_page = _arguments(answer).get("next")
            if not isinstance(next_page, dict):
                return reservations
            arguments = {"limit": PAGE_SIZE, **cast(dict[str, Any], next_page)}

    async def add(self, reservation: KeaReservation, user_context: dict[str, Any] | None = None) -> None:
        host: dict[str, Any] = {
            "subnet-id": reservation.subnet_id,
            "hw-address": reservation.mac,
            "ip-address": reservation.ip,
        }
        if user_context:
            host["user-context"] = user_context
        answer = await self.command("reservation-add", {"reservation": host, "operation-target": "database"})
        if answer["result"] != KEA_SUCCESS:
            raise KeaError(f"reservation-add {reservation}: {answer.get('text')}")

    async def delete(self, subnet_id: int, mac: str) -> bool:
        """Delete the reservation of `mac` in `subnet_id`. Return False if there was none."""
        answer = await self.command(
            "reservation-del",
            {
                "subnet-id": subnet_id,
                "identifier-type": "hw-address",
                "identifier": mac,
                "operation-target": "database",
            },
        )
        return answer["result"] == KEA_SUCCESS


def _parse_answer(command: str, response: httpx.Response) -> dict[str, Any]:
    if response.status_code != HTTP_OK:
        raise KeaError(f"{command}: HTTP {response.status_code}")
    try:
        payload: object = response.json()
    except ValueError as error:
        raise KeaError(f"{command}: invalid JSON") from error
    if isinstance(payload, list) and payload:
        payload = cast(list[object], payload)[0]
    if not isinstance(payload, dict):
        raise KeaError(f"{command}: unexpected answer")
    answer = cast(dict[str, Any], payload)
    result = answer.get("result")
    if result not in (KEA_SUCCESS, KEA_EMPTY):
        raise KeaError(f"{command}: result {result}: {answer.get('text')}")
    return answer


def _arguments(answer: dict[str, Any]) -> dict[str, Any]:
    arguments = answer.get("arguments")
    return cast(dict[str, Any], arguments) if isinstance(arguments, dict) else {}


def _parse_hosts(answer: dict[str, Any]) -> list[KeaReservation]:
    hosts = _arguments(answer).get("hosts")
    if not isinstance(hosts, list):
        return []
    reservations: list[KeaReservation] = []
    for raw in cast(list[object], hosts):
        if not isinstance(raw, dict):
            continue
        host = cast(dict[str, Any], raw)
        subnet_id, mac, ip = host.get("subnet-id"), host.get("hw-address"), host.get("ip-address")
        if isinstance(subnet_id, int) and isinstance(mac, str) and isinstance(ip, str):
            reservations.append(KeaReservation(subnet_id=subnet_id, mac=mac, ip=ip))
    return reservations


def kea_config_from_settings(urls: list[str] | None = None) -> KeaConfig:
    """Build the client configuration from the settings. Raise KeaError if a value is missing."""
    chosen = urls if urls else settings.kea_urls
    if not chosen:
        raise KeaError("Missing Kea configuration: KEA_API_URLS")
    if settings.kea_api_password is None:
        raise KeaError("Missing Kea configuration: KEA_API_PASSWORD")
    return KeaConfig(
        urls=tuple(chosen),
        user=settings.kea_api_user,
        password=settings.kea_api_password.get_secret_value(),
        ca_file=settings.kea_api_ca_file or None,
        timeout_seconds=settings.kea_api_timeout_seconds,
    )
