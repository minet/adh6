import { AuthConfig } from 'angular-oauth2-oidc';
import { environment } from '../../environments/environment';

const REDIRECT_URL = "https://" + window.location.host.toString() + "/dashboard";
const CLIENT_ID = "adh6";
const SCOPE = "profile roles";
// const OIDC = "false";
const RESPONSE_TYPE = "code";
// const DEBUG = "true";

export const authConfig: AuthConfig = {
  issuer: environment.SSO_URL,
  redirectUri: REDIRECT_URL,
  clientId: CLIENT_ID,
  scope: SCOPE,
  oidc: false,
  responseType: RESPONSE_TYPE,
  showDebugInformation: true,
  dummyClientSecret: "thisisneededforApereoCAS"
};
