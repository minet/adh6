"""
Logs repository.
"""

import logging
from typing import Any, cast

import dateutil.parser
from elastic_transport import ConnectionError as ElasticsearchConnectionError, ConnectionTimeout
from elasticsearch import AsyncElasticsearch

from adh6.config.configuration import settings
from adh6.constants import LOG_DEFAULT_LIMIT
from adh6.device.interfaces.logs_repository import LogEntry, LogsRepository
from adh6.entity import Device, Member
from adh6.exceptions import LogFetchError
from adh6.misc import get_mac_variations

logger = logging.getLogger(__name__)


class ElasticsearchLogsRepository(LogsRepository):
    """
    Interface to the log repository.
    """

    def __init__(self) -> None:
        self.elk_enabled = settings.elk_enabled
        self.es: AsyncElasticsearch | None = None

        if not self.elk_enabled:
            return

        if settings.elk_user and settings.elk_secret:
            self.es = AsyncElasticsearch(
                [host.strip() for host in settings.elk_hosts.split(",") if host.strip()],
                request_timeout=settings.elk_request_timeout_seconds,
                basic_auth=(settings.elk_user, settings.elk_secret),
            )
        else:
            self.es = AsyncElasticsearch(
                [host.strip() for host in settings.elk_hosts.split(",") if host.strip()],
                request_timeout=settings.elk_request_timeout_seconds,
            )

    async def close(self) -> None:
        """Close connections owned by the shared Elasticsearch client."""
        if self.es is not None:
            await self.es.close()

    async def get(
        self,
        member: Member,
        devices: list[Device] | None = None,
        limit: int = LOG_DEFAULT_LIMIT,
        offset: int = 0,
        dhcp: bool = False,
    ) -> tuple[list[LogEntry], int]:
        """
        Get the logs related to the username and to the devices.
        :param member: Member object
        :param devices: MAC addresses of the devices
        :param limit: limit result
        :param offset: offset for pagination
        :param dhcp: allow to query DHCP logs or not
        :return: tuple of (logs, total_count)
        """
        if not self.elk_enabled:
            # Mock data for development
            # Generate a large number of mock logs to test pagination
            mock_logs: list[LogEntry] = [
                (
                    dateutil.parser.parse(f"2024-01-{(i % 31) + 1:02d}T10:{(i % 60):02d}:00Z"),
                    f"test_log_{i}",
                )
                for i in range(1, 1001)
            ]
            paginated_logs = mock_logs[offset : offset + limit]
            return paginated_logs, len(mock_logs)

        should: list[dict[str, Any]] = [
            {"match_phrase": {"src_mac": variation}}
            for device in devices or []
            for variation in get_mac_variations(device.mac)
        ]
        bool_query: dict[str, Any] = {"should": should, "minimum_should_match": 1}
        if not dhcp:
            bool_query["filter"] = {"match": {"program": "radiusd"}}

        try:
            if self.es is None:
                raise LogFetchError
            response = await self.es.search(
                index="*",
                query={"constant_score": {"filter": {"bool": bool_query}}},
                sort={"@timestamp": "desc"},
                source_includes=["@timestamp", "message", "program", "src_mac"],
                size=limit,
                from_=offset,
                track_total_hits=True,
            )
        except (ElasticsearchConnectionError, ConnectionTimeout) as exc:
            logger.warning("Elasticsearch is unavailable while fetching member logs", exc_info=True)
            raise LogFetchError from exc
        response_data = cast(dict[str, Any], response)
        hits = response_data["hits"]
        total_count = hits["total"]["value"]
        logs: list[LogEntry] = [
            (dateutil.parser.parse(hit["_source"]["@timestamp"]), str(hit["_source"]["message"]))
            for hit in hits["hits"]
        ]
        return logs, total_count
