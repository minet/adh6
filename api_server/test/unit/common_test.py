import os

import adh6.server as server
import pytest


def test_server():
    os.environ["ENVIRONMENT"] = "default"

    with pytest.raises(EnvironmentError):
        server.init()
