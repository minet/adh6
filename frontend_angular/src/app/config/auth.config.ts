import { AuthConfig } from 'angular-oauth2-oidc';
const SSO_URL = "https://cas.minet.net/oidc";
const REDIRECT_URL = "https://" + window.location.host.toString() + "/portail";
const CLIENT_ID = "adh6";
const SCOPE = "profile";
// const OIDC = "false";
const RESPONSE_TYPE = "code";
// const DEBUG = "true";

export const authConfig: AuthConfig = {
  issuer: SSO_URL,
  redirectUri: REDIRECT_URL,
  clientId: CLIENT_ID,
  scope: SCOPE,
  oidc: false,
  responseType: RESPONSE_TYPE,
  showDebugInformation: true,
  dummyClientSecret: "thisisneededforApereoCAS"
};
