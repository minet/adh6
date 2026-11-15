import json

import httpx
import pytest
from adh6.kea.client import KeaClient, KeaConfig, KeaError, KeaReservation, KeaUnavailableError

KEA1 = "https://kea1:8443/"
KEA2 = "https://kea2:8443/"


def config(*urls: str) -> KeaConfig:
    return KeaConfig(urls=urls or (KEA1, KEA2), user="adh6", password="secret")


def answer(result: int, text: str = "", arguments: dict | None = None) -> httpx.Response:
    body: dict = {"result": result, "text": text}
    if arguments is not None:
        body["arguments"] = arguments
    # Kea's HTTP control socket wraps the answer in a list.
    return httpx.Response(200, json=[body])


async def test_sends_json_with_basic_auth_and_operation_target():
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return answer(0, "Host added.")

    async with KeaClient(config(), transport=httpx.MockTransport(handler)) as client:
        await client.add(KeaReservation(41, "aa:bb:cc:dd:ee:01", "157.159.41.10"), {"adh6_device": 1})

    request = seen[0]
    assert request.headers["content-type"] == "application/json"
    assert request.headers["authorization"].startswith("Basic ")
    assert json.loads(request.content) == {
        "command": "reservation-add",
        "arguments": {
            "reservation": {
                "subnet-id": 41,
                "hw-address": "aa:bb:cc:dd:ee:01",
                "ip-address": "157.159.41.10",
                "user-context": {"adh6_device": 1},
            },
            "operation-target": "database",
        },
    }


async def test_fails_over_to_the_next_server_and_sticks_to_it():
    hosts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        if request.url.host == "kea1":
            raise httpx.ConnectError("down", request=request)
        return answer(3, "0 IPv4 host(s) found.", {"hosts": []})

    async with KeaClient(config(), transport=httpx.MockTransport(handler)) as client:
        assert await client.reservations_for_mac("aa:bb:cc:dd:ee:01") == []
        assert await client.reservations_for_mac("aa:bb:cc:dd:ee:02") == []

    assert hosts == ["kea1", "kea2", "kea2"]


async def test_no_server_answering_raises_unavailable():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    async with KeaClient(config(), transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(KeaUnavailableError):
            await client.delete(41, "aa:bb:cc:dd:ee:01")


async def test_refused_command_raises_without_trying_the_other_server():
    hosts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        return answer(1, "IPv4 subnet with ID of '999' is not configured")

    async with KeaClient(config(), transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(KeaError, match="999"):
            await client.add(KeaReservation(999, "aa:bb:cc:dd:ee:01", "10.0.0.1"))

    assert hosts == ["kea1"]


async def test_unauthorized_is_an_error():
    async with KeaClient(config(), transport=httpx.MockTransport(lambda r: httpx.Response(401))) as client:
        with pytest.raises(KeaError, match="401"):
            await client.reservations_for_mac("aa:bb:cc:dd:ee:01")


async def test_delete_reports_whether_something_was_deleted():
    results = iter([answer(0, "Host deleted."), answer(3, "Host not deleted (not found).")])
    async with KeaClient(config(), transport=httpx.MockTransport(lambda r: next(results))) as client:
        assert await client.delete(41, "aa:bb:cc:dd:ee:01") is True
        assert await client.delete(41, "aa:bb:cc:dd:ee:01") is False


async def test_all_reservations_follows_the_pages():
    host = {"subnet-id": 41, "hw-address": "aa:bb:cc:dd:ee:01", "ip-address": "157.159.41.10"}
    other = {"subnet-id": 1000, "hw-address": "aa:bb:cc:dd:ee:02", "ip-address": "10.42.0.18"}
    pages = iter(
        [
            answer(0, "", {"count": 1, "hosts": [host], "next": {"from": 1, "source-index": 1}}),
            answer(0, "", {"count": 1, "hosts": [other], "next": {"from": 2, "source-index": 1}}),
            answer(3, "0 IPv4 host(s) found.", {"count": 0, "hosts": []}),
        ]
    )
    sent: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content)["arguments"])
        return next(pages)

    async with KeaClient(config(), transport=httpx.MockTransport(handler)) as client:
        reservations = await client.all_reservations()

    assert reservations == [
        KeaReservation(41, "aa:bb:cc:dd:ee:01", "157.159.41.10"),
        KeaReservation(1000, "aa:bb:cc:dd:ee:02", "10.42.0.18"),
    ]
    assert sent[1] == {"limit": 1000, "from": 1, "source-index": 1}


async def test_must_be_used_as_a_context_manager():
    with pytest.raises(RuntimeError):
        await KeaClient(config()).reservations_for_mac("aa:bb:cc:dd:ee:01")
