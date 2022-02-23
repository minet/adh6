import pytest
import common

def test_common():
    import os
    del os.environ["ENVIRONMENT"]
    with pytest.raises(EnvironmentError):
        common.init()