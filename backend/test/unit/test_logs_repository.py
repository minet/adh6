from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from adh6.config.configuration import settings
from adh6.device.storage.logs_repository import ElasticsearchLogsRepository


@pytest.mark.asyncio
async def test_elasticsearch_repository_uses_async_modern_client(monkeypatch):
    monkeypatch.setattr(settings, "elk_enabled", True)
    monkeypatch.setattr(settings, "elk_hosts", " http://one:9200, http://two:9200 ")
    monkeypatch.setattr(settings, "elk_user", "user")
    monkeypatch.setattr(settings, "elk_secret", "secret")

    with patch("adh6.device.storage.logs_repository.AsyncElasticsearch") as client_class:
        client = client_class.return_value
        client.search = AsyncMock(
            return_value={
                "hits": {
                    "total": {"value": 1},
                    "hits": [
                        {
                            "_source": {
                                "@timestamp": "2026-01-01T00:00:00Z",
                                "message": "connected",
                            }
                        }
                    ],
                }
            }
        )
        client.close = AsyncMock()

        repository = ElasticsearchLogsRepository()
        logs, total = await repository.get(member=MagicMock(), devices=[])
        await repository.close()

    client_class.assert_called_once_with(
        ["http://one:9200", "http://two:9200"],
        basic_auth=("user", "secret"),
    )
    search_call = client.search.await_args
    assert search_call is not None
    assert search_call.kwargs["track_total_hits"] is True
    assert "body" not in search_call.kwargs
    assert total == 1
    assert logs[0][1] == "connected"
    client.close.assert_awaited_once()
