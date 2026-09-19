import json
from unittest.mock import MagicMock

import pytest
from adh6.exceptions import LogFetchError
from adh6.main import handle_log_fetch_error


@pytest.mark.asyncio
async def test_log_fetch_error_returns_service_unavailable():
    response = await handle_log_fetch_error(MagicMock(), LogFetchError("internal transport details"))

    assert response.status_code == 503
    assert response.headers["retry-after"] == "30"
    assert json.loads(bytes(response.body)) == {"detail": "Log service temporarily unavailable"}
