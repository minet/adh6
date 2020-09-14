import {AuthConfig} from 'angular-oauth2-oidc';

export const authConfig: AuthConfig = {
  redirectUri: '${ADH6_URL}',
  clientId: 'adh6',
  scope: 'openid profile offline_access roles',
  issuer: '${SSO_OAUTH2}',
  oidc: false,
  responseType: 'code',
  showDebugInformation: true,
};

export const authBypass = ${BYPASS_AUTH};
