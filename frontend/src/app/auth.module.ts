import {NgModule} from "@angular/core";
import {AuthModule} from "angular-auth-oidc-client";
import {environment} from "../environments/environment";

@NgModule({
  imports: [
    AuthModule.forRoot({
      config: {
        secureRoutes: ["/"],
        authority: environment.SSO_URL,
        redirectUrl: window.location.href,
        postLogoutRedirectUri: window.location.origin,
        clientId: environment.SSO_CLIENT_ID,
        scope: environment.SSO_SCOPE,
        responseType: environment.SSO_RESPONSE_TYPE,
        useRefreshToken: true,
        renewTimeBeforeTokenExpiresInSeconds: 30,
        logLevel: environment.LOG_LEVEL,
      },
    }),
  ],
  exports: [AuthModule],
})
export class AuthConfigModule {}
