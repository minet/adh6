import {LogLevel} from "angular-auth-oidc-client";

export const environment = {
  production: true,
  API_BASE_PATH: "https://" + window.location.host.toString() + "/api",
  SSO_URL: "https://keycloak.minet.net/realms/MiNET",
  SSO_CLIENT_ID: "adh6-keycloak",
  SSO_SCOPE: "openid offline_access",
  SSO_RESPONSE_TYPE: "code",
  LOG_LEVEL: LogLevel.Warn,
};
