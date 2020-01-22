import {AuthConfig} from 'angular-oauth2-oidc';

export const authConfig: AuthConfig = {
  //loginUrl: '${SSO_AUTHORIZE}',
  //logoutUrl: '${SSO_LOGOUT}',
  redirectUri: '${ADH6_URL}',
  //userinfoEndpoint: 'https://cas.minet.net/oidc/profile',
  clientId: 'adh6',
  scope: 'openid profile offline_access groups',
  issuer: 'https://cas.minet.net/oidc',
  oidc: true,
};

export const authBypass = ${BYPASS_AUTH};
