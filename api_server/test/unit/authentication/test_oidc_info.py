"""Tests for OIDC authentication information extraction."""

from unittest.mock import MagicMock, patch

import pytest
from adh6.authentication.enums import AuthenticationMethod, Roles
from adh6.authentication.oidc.oidc_info import oidc_info
from adh6.entity import RoleMapping
from connexion.exceptions import Unauthorized
from flask import Flask
from jwcrypto.jwt import JWTExpired, JWTInvalidClaimFormat, JWTMissingClaim


class TestOidcInfo:
    """Test cases for the oidc_info function."""

    @pytest.fixture
    def mock_app_context(self):
        """Create a mock Flask app context with Keycloak client."""
        app = Flask(__name__)
        with app.app_context():
            # Mock Keycloak client
            mock_keycloak = MagicMock()
            app.config["KEYCLOAK_CLIENT"] = mock_keycloak
            yield mock_keycloak

    @pytest.fixture
    def mock_role_repository(self):
        """Create a mock role repository."""
        with patch("adh6.authentication.oidc.oidc_info.role_repository") as mock_repo:
            yield mock_repo

    @pytest.fixture
    def valid_token_data(self):
        """Sample valid token data."""
        return {
            "adh6_id": 123,
            "preferred_username": "testuser",
            "groups": ["/admin", "/network_admin", "/treso"],
            "sub": "user-uuid-123",
            "iat": 1234567890,
            "exp": 9999999999,
        }

    @pytest.fixture
    def valid_token_data_no_adh6_id(self):
        """Sample valid token data without adh6_id."""
        return {
            "preferred_username": "testuser",
            "groups": ["/admin", "/network_admin"],
            "sub": "user-uuid-123",
            "iat": 1234567890,
            "exp": 9999999999,
        }

    def test_valid_token_with_adh6_id(self, mock_app_context, mock_role_repository, valid_token_data):
        """Test successful authentication with a valid token containing adh6_id."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = valid_token_data

        # Mock role repository responses
        oidc_roles = [
            RoleMapping(role=Roles.ADMIN_READ, authentication=AuthenticationMethod.OIDC.value, identifier="admin"),
            RoleMapping(
                role=Roles.NETWORK_READ, authentication=AuthenticationMethod.OIDC.value, identifier="network_admin"
            ),
        ]
        user_roles = [
            RoleMapping(role=Roles.USER, authentication=AuthenticationMethod.USER.value, identifier="testuser"),
        ]

        mock_role_repository.find.side_effect = [
            (oidc_roles, len(oidc_roles)),  # First call for OIDC groups
            (user_roles, len(user_roles)),  # Second call for username
        ]

        # Execute
        result = oidc_info("valid_token_123")

        # Assert
        assert result is not None
        assert result["uid"] == 123
        assert result["username"] == "testuser"
        assert result["groups"] == ["admin", "network_admin", "treso"]
        assert Roles.USER.value in result["scope"]
        assert Roles.ADMIN_READ in result["scope"]  # Role enum object, not .value
        assert Roles.NETWORK_READ in result["scope"]
        assert Roles.USER in result["scope"]  # Role enum object, not .value

        # Verify calls
        mock_keycloak.decode_token.assert_called_once_with("valid_token_123")
        assert mock_role_repository.find.call_count == 2

    def test_valid_token_without_adh6_id(self, mock_app_context, mock_role_repository, valid_token_data_no_adh6_id):
        """Test successful authentication with a valid token without adh6_id, using username lookup."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = valid_token_data_no_adh6_id

        # Mock user_id_from_username lookup
        mock_role_repository.user_id_from_username.return_value = 456

        # Mock role repository responses
        oidc_roles = [
            RoleMapping(role=Roles.ADMIN_WRITE, authentication=AuthenticationMethod.OIDC.value, identifier="admin"),
        ]
        user_roles = [
            RoleMapping(role=Roles.USER, authentication=AuthenticationMethod.USER.value, identifier="testuser"),
        ]

        mock_role_repository.find.side_effect = [
            (oidc_roles, len(oidc_roles)),  # First call for OIDC groups
            (user_roles, len(user_roles)),  # Second call for username
        ]

        # Execute
        result = oidc_info("valid_token_456")

        # Assert
        assert result is not None
        assert result["uid"] == 456
        assert result["username"] == "testuser"
        assert result["groups"] == ["admin", "network_admin"]
        assert Roles.USER.value in result["scope"]
        assert Roles.ADMIN_WRITE in result["scope"]  # Role enum object, not .value

        # Verify username lookup was called
        mock_role_repository.user_id_from_username.assert_called_once_with(login="testuser")

    def test_required_scopes_valid_fails_due_to_mixed_types(
        self, mock_app_context, mock_role_repository, valid_token_data
    ):
        """Test that required scopes validation currently fails due to mixing enum objects and strings in scope.

        This test documents a bug in the current implementation where scope contains mixed types
        (Roles.USER.value as string + enum objects from roles), making validation inconsistent.
        """
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = valid_token_data

        # Mock role repository to return admin roles
        admin_roles = [
            RoleMapping(role=Roles.ADMIN_READ, authentication=AuthenticationMethod.OIDC.value, identifier="admin"),
        ]
        user_roles = [
            RoleMapping(role=Roles.USER, authentication=AuthenticationMethod.USER.value, identifier="testuser"),
        ]

        mock_role_repository.find.side_effect = [
            (admin_roles, len(admin_roles)),
            (user_roles, len(user_roles)),
        ]

        # Execute - currently fails due to enum/string type mismatch in scope validation
        # Note: This test expects the scope validation to work with enum objects vs string values
        with pytest.raises(Unauthorized, match="missing required scopes"):
            oidc_info("valid_token_123", required_scopes=[Roles.USER.value, Roles.ADMIN_READ.value])

    def test_required_scopes_work_with_enum_objects(self, mock_app_context, mock_role_repository, valid_token_data):
        """Test that required scopes validation works when using enum objects (not documented behavior)."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = valid_token_data

        # Mock role repository to return admin roles
        admin_roles = [
            RoleMapping(role=Roles.ADMIN_READ, authentication=AuthenticationMethod.OIDC.value, identifier="admin"),
        ]
        user_roles = [
            RoleMapping(role=Roles.USER, authentication=AuthenticationMethod.USER.value, identifier="testuser"),
        ]

        mock_role_repository.find.side_effect = [
            (admin_roles, len(admin_roles)),
            (user_roles, len(user_roles)),
        ]

        # Execute - works when using enum objects for required_scopes (matching scope content)
        result = oidc_info("valid_token_123", required_scopes=[Roles.USER.value, Roles.ADMIN_READ])

        # Assert
        assert result is not None
        assert result["uid"] == 123

    def test_required_scopes_invalid(self, mock_app_context, mock_role_repository, valid_token_data):
        """Test that authentication fails when required scopes are missing."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = valid_token_data

        # Mock role repository to return only basic user role
        user_roles = [
            RoleMapping(role=Roles.USER, authentication=AuthenticationMethod.USER.value, identifier="testuser"),
        ]

        mock_role_repository.find.side_effect = [
            ([], 0),  # No OIDC roles
            (user_roles, len(user_roles)),  # Only basic user role
        ]

        # Execute - should fail because user lacks admin role
        with pytest.raises(Unauthorized, match="missing required scopes"):
            oidc_info("valid_token_123", required_scopes=[Roles.USER.value, Roles.ADMIN_READ.value])

    def test_invalid_token_not_string(self, mock_app_context, mock_role_repository):
        """Test that authentication fails for non-string tokens."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.side_effect = JWTInvalidClaimFormat("Invalid token format")

        # Execute & Assert
        with pytest.raises(Unauthorized, match="Invalid OIDC token.*InvalidClaimFormat"):
            oidc_info(123)  # Pass non-string token

    def test_expired_token(self, mock_app_context, mock_role_repository):
        """Test that authentication fails for expired tokens."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.side_effect = JWTExpired("Token has expired")

        # Execute & Assert
        with pytest.raises(Unauthorized, match="Invalid OIDC token.*Expired"):
            oidc_info("expired_token_123")

    def test_missing_claim_token(self, mock_app_context, mock_role_repository):
        """Test that authentication fails for tokens with missing claims."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.side_effect = JWTMissingClaim("Missing required claim")

        # Execute & Assert
        with pytest.raises(Unauthorized, match="Invalid OIDC token.*MissingClaim"):
            oidc_info("incomplete_token_123")

    def test_tampered_token_invalid_signature(self, mock_app_context, mock_role_repository):
        """Test that authentication fails for tokens with invalid signatures (tampered)."""
        # Setup - simulate a tampered token that Keycloak rejects
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.side_effect = JWTInvalidClaimFormat("Invalid signature")

        # Execute & Assert
        with pytest.raises(Unauthorized, match="Invalid OIDC token.*InvalidClaimFormat"):
            oidc_info("tampered.token.with.invalid.signature")

    def test_empty_token_data(self, mock_app_context, mock_role_repository):
        """Test that authentication fails when token decoding returns no data."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = None

        # Execute & Assert
        with pytest.raises(Unauthorized, match="Invalid OIDC token: no data found"):
            oidc_info("empty_token")

    def test_malformed_token_data(self, mock_app_context, mock_role_repository):
        """Test that authentication fails when token data is not a dictionary."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = "not_a_dict"

        # Execute & Assert
        with pytest.raises(Unauthorized, match="Invalid OIDC token: the data is not properly formatted"):
            oidc_info("malformed_token")

    def test_token_without_username_or_id(self, mock_app_context, mock_role_repository):
        """Test token processing when neither adh6_id nor preferred_username is present."""
        # Setup
        mock_keycloak = mock_app_context
        token_data = {
            "groups": ["/admin"],
            "sub": "user-uuid-123",
        }
        mock_keycloak.decode_token.return_value = token_data

        # Mock role repository responses
        oidc_roles = [
            RoleMapping(role=Roles.ADMIN_READ, authentication=AuthenticationMethod.OIDC.value, identifier="admin"),
        ]

        mock_role_repository.find.side_effect = [
            (oidc_roles, len(oidc_roles)),  # OIDC groups
            ([], 0),  # No username-based roles
        ]

        # Execute
        result = oidc_info("token_without_user_info")

        # Assert
        assert result is not None
        assert result["uid"] is None  # No user ID available
        assert result["username"] is None
        assert result["groups"] == ["admin"]
        assert Roles.USER.value in result["scope"]
        assert Roles.ADMIN_READ in result["scope"]  # Role enum object, not .value

    def test_groups_stripping_leading_slash(self, mock_app_context, mock_role_repository):
        """Test that leading slashes are properly stripped from group names."""
        # Setup
        mock_keycloak = mock_app_context
        token_data = {
            "adh6_id": 123,
            "preferred_username": "testuser",
            "groups": ["/admin", "//double_slash", "no_slash", None],  # Mix of formats including None
        }
        mock_keycloak.decode_token.return_value = token_data

        mock_role_repository.find.return_value = ([], 0)

        # Execute
        result = oidc_info("token_with_various_groups")
        if result is None:
            pytest.fail("oidc_info returned None, expected a valid result")

        # Assert
        assert result["groups"] == ["admin", "double_slash", "no_slash"]  # Leading slashes stripped, None filtered out

    def test_no_groups_in_token(self, mock_app_context, mock_role_repository):
        """Test token processing when no groups are present."""
        # Setup
        mock_keycloak = mock_app_context
        token_data = {
            "adh6_id": 123,
            "preferred_username": "testuser",
            # No groups field
        }
        mock_keycloak.decode_token.return_value = token_data

        user_roles = [
            RoleMapping(role=Roles.USER, authentication=AuthenticationMethod.USER.value, identifier="testuser"),
        ]

        mock_role_repository.find.side_effect = [
            ([], 0),  # No OIDC roles because no groups
            (user_roles, len(user_roles)),  # Username-based roles
        ]

        # Execute
        result = oidc_info("token_without_groups")

        # Assert
        assert result is not None
        assert result["groups"] == []
        assert Roles.USER.value in result["scope"]

    def test_invalid_required_scopes_type(self, mock_app_context, mock_role_repository, valid_token_data):
        """Test that authentication fails when required_scopes is not a list."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = valid_token_data

        mock_role_repository.find.return_value = ([], 0)

        # Execute & Assert
        with pytest.raises(Unauthorized, match="Invalid OIDC token: required scopes must be a list"):
            oidc_info("valid_token_123", required_scopes="not_a_list")

    @patch("builtins.print")  # Mock print to test debug output
    def test_debug_output(self, mock_print, mock_app_context, mock_role_repository, valid_token_data):
        """Test that debug information is printed during token processing."""
        # Setup
        mock_keycloak = mock_app_context
        mock_keycloak.decode_token.return_value = valid_token_data

        mock_role_repository.find.return_value = ([], 0)

        # Execute
        oidc_info("valid_token_123")

        # Assert that print was called for debugging
        assert mock_print.call_count >= 2  # Should print token_data and result

        # Check that the printed content contains expected debug info
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("oidc_info token_data:" in str(call) for call in print_calls)
        assert any("oidc_info result:" in str(call) for call in print_calls)
