# coding=utf-8
""" Use cases (business rule layer) of everything related to transactions. """
from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants

from src.entity import AbstractMember
from src.interface_adapter.sql.model.database import Database as Db
from src.use_case.interface.member_repository import MemberRepository
from src.use_case.interface.oauth_repository import OAuthRepository
from src.util.context import build_context


class OAuthManager:
    """
    Implements all the use cases related to the OAuth server
    """

    def __init__(self,
                 oauth_repository: OAuthRepository, member_repository: MemberRepository,
                 oauth: OAuth
                 ):
        self.oauth_repository = oauth_repository
        self.member_repository = member_repository
        self.oauth = oauth

        def query_client(client_id):
            s = Db.get_db().get_session()
            ctx = build_context(session=s)
            client = self.oauth_repository.get_client(ctx, client_id=client_id)
            s.close()
            return client

        def save_token(token, request):
            s = Db.get_db().get_session()
            ctx = build_context(session=s)
            if request.user:
                username = request.user.username
            else:
                username = None
            client = request.client
            self.oauth_repository.create_token(ctx, client_id=client.client_id, username=username, **token)
            s.commit()
            s.close()
        self.authorization = AuthorizationServer(
            query_client=query_client,
            save_token=save_token,
        )

    def init_app(self, app):
        self.authorization.init_app(app)
        self.authorization.register_grant(grants.ImplicitGrant)

    def get_token(self, ctx, access_token):
        token = self.oauth_repository.get_token(ctx, access_token=access_token)
        return {
            'id': token.user.login,
            'given_name': token.user.prenom + ' ' + token.user.nom,
            'sub': token.user.login,
            'scope': token.scope
        }

    def create_authorization_response(self, ctx, request=None, grant_user=None):
        users, _ = self.member_repository.search_by(ctx, filter_=AbstractMember(username=grant_user))
        return self.authorization.create_authorization_response(request=request, grant_user=users[0])