from unittest.mock import MagicMock

import pytest
from adh6.security import require_role_or_ownership
from fastapi import HTTPException, Request, status


class TestRequireRoleOrOwnership:
    def test_has_role(self):
        # Given
        request = MagicMock(spec=Request)
        request.state.token_info = {"scope": ["admin:write"]}

        # When / Then (should not raise)
        require_role_or_ownership(request, "admin:write")

    def test_has_ownership(self):
        # Given
        request = MagicMock(spec=Request)
        request.state.token_info = {"uid": 123, "scope": []}

        # When / Then (should not raise)
        require_role_or_ownership(request, "admin:write", owner_id=123)

    def test_insufficient_permissions_oidc(self):
        # Given
        request = MagicMock(spec=Request)
        request.state.token_info = {"uid": 456, "scope": ["user"], "auth_method": "oidc"}

        # When / Then
        with pytest.raises(HTTPException) as excinfo:
            require_role_or_ownership(request, "admin:write", owner_id=123)
        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN

    def test_insufficient_permissions_api_key(self):
        # Given
        request = MagicMock(spec=Request)
        request.state.token_info = {"uid": None, "scope": ["user"], "auth_method": "api_key"}

        # When / Then
        with pytest.raises(HTTPException) as excinfo:
            require_role_or_ownership(request, "admin:write")
        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
