import { NgModule } from '@angular/core';
import { AuthModule, LogLevel } from 'angular-auth-oidc-client';
import { environment } from '../environments/environment';

@NgModule({
  imports: [
    AuthModule.forRoot({
      config: {
        secureRoutes: ['/'],
        authority: environment.SSO_URL,
        redirectUrl: window.location.href,
        postLogoutRedirectUri: window.location.origin,
        clientId: 'adh6',
        scope: 'openid profile groups',
        responseType: 'id_token token',
        useRefreshToken: true,
        renewTimeBeforeTokenExpiresInSeconds: 30,
        logLevel: LogLevel.Debug,
      },
    }),
  ],
  exports: [AuthModule],
})
export class AuthConfigModule {}