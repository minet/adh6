import {AuthConfig} from 'angular-oauth2-oidc';

export const authConfig: AuthConfig = {
  redirectUri: '${ADH6_URL}',
  clientId: 'adh6_dev',
  scope: 'openid profile offline_access roles',
  issuer: '${SSO_OAUTH2}',
  oidc: false,
};

export const authBypass = ${BYPASS_AUTH};
