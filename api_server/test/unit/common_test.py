import pytest
import common

def test_common():
    import os
    os.environ["ENVIRONMENT"] = "default"
    with pytest.raises(EnvironmentError):
        common.init()
