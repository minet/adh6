import adh6.server as server
import pytest


def test_server():
    import os

    os.environ["ENVIRONMENT"] = "default"
    with pytest.raises(EnvironmentError):
        server.init()
