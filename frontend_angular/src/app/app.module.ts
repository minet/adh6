import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { ApiModule, Device, Member, Room, Port, Transaction, Account, Configuration, ConfigurationParameters, Membership } from './api';
import { NavbarComponent } from './navbar/navbar.component';
import { AuthConfig, OAuthModule, OAuthService, OAuthStorage } from 'angular-oauth2-oidc';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NotifInterceptor } from './http-interceptor/notif-interceptor';
import { environment } from '../environments/environment';
import { ErrorPageComponent } from './error-page/error-page.component';
import { Ability, AbilityClass, InferSubjects, PureAbility } from '@casl/ability';
import { AbilityModule } from '@casl/angular';
import { authConfig } from './config/auth.config';
import '@angular/common/locales/global/fr';
import '@angular/common/locales/global/en';
import { FooterComponent } from './footer/footer.component';
import { VerticalNavbarComponent } from './vertical-navbar/vertical-navbar.component';
import { PortailComponent } from './portail/portail.component';

type Actions = 'manage' | 'create' | 'read' | 'update' | 'delete' | 'free';
type Subjects = InferSubjects<Member> | InferSubjects<Transaction> | InferSubjects<Device> | InferSubjects<Account> | InferSubjects<Room> | InferSubjects<Port> | InferSubjects<Membership> | "all";

export type AppAbility = Ability<[Actions, Subjects]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

function load(oAuthService: OAuthService): Configuration {
  let params: ConfigurationParameters =
  {
    basePath: environment.API_BASE_PATH,
    accessToken: oAuthService.getAccessToken(),
    apiKeys: {}
  };
  return new Configuration(params);
}

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    ErrorPageComponent,
    FooterComponent,
    VerticalNavbarComponent,
    PortailComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    OAuthModule.forRoot(),
    HttpClientModule,
    AbilityModule,
    ApiModule,
  ],
  providers: [
    AppComponent,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: NotifInterceptor,
      multi: true
    },
    { provide: OAuthStorage, useFactory: (): OAuthStorage => localStorage },
    { provide: AuthConfig, useValue: authConfig },
    {
      provide: AppAbility, useValue: new AppAbility()
    },
    { provide: PureAbility, useExisting: AppAbility },
    {
      provide: Configuration,
      useFactory: load,
      deps: [OAuthService],
      multi: false
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
