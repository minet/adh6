# coding=utf-8
import base64
import json
import urllib

from authlib.oauth2 import OAuth2Error, OAuth2Request
from flask import redirect, request, session, current_app

from src.interface_adapter.http_api.decorator.with_context import with_context
from src.interface_adapter.sql.decorator.sql_session import require_sql
from src.use_case.oauth_manager import OAuthManager
from src.util.context import log_extra
from src.util.log import LOG


class OAuthHandler:
    def __init__(self, oauth_manager: OAuthManager):
        self.oauth_manager = oauth_manager

    @with_context
    @require_sql
    def authorize_get(self, ctx, code=None, return_to=None):
        LOG.debug("http_oauth_authorize_get_called", extra=log_extra(ctx))
        if code is None:
            ret = self.oauth_manager.oauth.cas.authorize_redirect(
                current_app.config["AUTH_AUTHORIZE_ADDRESS"] + '?' + urllib.parse.urlencode({'return_to': ctx['url']}))
            return ret, 302
        else:
            token = self.oauth_manager.oauth.cas.authorize_access_token()
            userinfo = self.oauth_manager.oauth.cas.parse_id_token(token)
            LOG.debug("http_oauth_authorize_get_called_bis",
                      extra=log_extra(ctx, userinfo=userinfo, return_to=return_to))
            try:
                req = OAuth2Request('GET', return_to, None, [])
                grant = self.oauth_manager.authorization.validate_consent_request(request=req, end_user=userinfo['sub'])
            except OAuth2Error as error:
                return {'error': str(error.error), 'description': str(error.description)}, 400

            if grant.client.bypass_consent:
                req = OAuth2Request('GET', return_to, None, [])
                return self.oauth_manager.create_authorization_response(ctx, request=req, grant_user=userinfo['sub']), 302
            else:
                session['username'] = userinfo['sub']

                url = current_app.config["AUTH_CONSENT_ADDRESS"] + '#' + base64.b64encode(
                    json.dumps(_map_authorization_to_http_response(return_to, userinfo, grant)).encode('utf-8')).decode(
                    'utf-8')
                return redirect(url), 302

    @with_context
    @require_sql
    def profile_get(self, ctx):
        access_token = request.headers['Authorization'].split("Bearer ")[1]
        LOG.debug("http_oauth_profile_get_called", extra=log_extra(ctx, authorization=access_token))
        return self.oauth_manager.get_token(ctx, access_token), 200

    @with_context
    def oauth2_config(self, ctx):
        return current_app.config["AUTH_METADATA"], 200

    @with_context
    @require_sql
    def authorize_post(self, ctx):
        LOG.debug("http_oauth_authorize_post_called", extra=log_extra(ctx))
        return self.oauth_manager.create_authorization_response(ctx, grant_user=session['username']), 302

    @with_context
    @require_sql
    def token_post(self, ctx):
        LOG.debug("http_oauth_token_post_called", extra=log_extra(ctx))
        return self.oauth_manager.authorization.create_token_response()


def _map_authorization_to_http_response(uri, userinfo, grant):
    return {
        "username": userinfo['sub'],
        'scope': grant.request.scope,
        'client_name': grant.client.client_id,
        'return_uri': uri
    }
