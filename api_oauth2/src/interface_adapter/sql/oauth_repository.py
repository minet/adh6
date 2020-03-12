# coding=utf-8
"""
Implements everything related to actions on the SQL database.
"""

from src.constants import CTX_SQL_SESSION
from src.exceptions import NotFoundError
from src.interface_adapter.sql.model.models import OAuth2AuthorizationCode, OAuth2Client, Adherent, OAuth2Token
from src.use_case.interface.oauth_repository import OAuthRepository
from src.util.context import log_extra
from src.util.log import LOG


class OAuthSQLRepository(OAuthRepository):

    def create_client(self, ctx, token_endpoint_auth_method=None, client_id=None):
        pass

    def get_client(self, ctx, client_id=None):
        LOG.debug("sql_oauth_repository_get_client_called",
                  extra=log_extra(ctx, client_id=client_id))
        s = ctx.get(CTX_SQL_SESSION)

        client = s.query(OAuth2Client).filter(OAuth2Client.client_id == client_id).one_or_none()
        if client is None:
            raise NotFoundError("Client not found")

        return client

    def delete_client(self, ctx, client_id=None):
        pass

    def create_token(self, ctx, client_id=None, username=None, access_token=None, expires_in=None, scope=None,
                     refresh_token=None, token_type=None):
        LOG.debug("sql_oauth_repository_create_token_called",
                  extra=log_extra(ctx, username=username, client_id=client_id, scope=scope, access_token=access_token,
                                  expires_in=expires_in, refresh_token=refresh_token, token_type=token_type))
        s = ctx.get(CTX_SQL_SESSION)

        user = s.query(Adherent).filter(Adherent.login == username).one_or_none()

        if user is None:
            raise NotFoundError("User not found")

        token = OAuth2Token(
            expires_in=expires_in,
            client_id=client_id,
            access_token=access_token,
            revoked=False,
            refresh_token=refresh_token,
            token_type=token_type,
            scope=scope,
            user=user
        )

        s.add(token)

    def get_token(self, ctx, access_token=None):
        LOG.debug("sql_oauth_repository_get_token_called", extra=log_extra(ctx, access_token=access_token))
        s = ctx.get(CTX_SQL_SESSION)

        token = s.query(OAuth2Token).filter(OAuth2Token.access_token == access_token).one_or_none()
        if token is None:
            raise NotFoundError("Token not found")

        return token
