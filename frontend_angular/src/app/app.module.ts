import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {AppComponent} from './app.component';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {AppRoutingModule} from './app-routing.module';
import {ApiModule, Device, Member, Room, Port, ModelSwitch, Transaction, Account, Configuration, ConfigurationParameters} from './api';
import {GlobalSearchComponent} from './global-search/global-search.component';
import {NavbarComponent} from './navbar/navbar.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {AuthConfig, OAuthModule, OAuthService, OAuthStorage} from 'angular-oauth2-oidc';
import {BsDropdownModule} from 'ngx-bootstrap/dropdown';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {NotifInterceptor} from './http-interceptor/notif-interceptor';
import {environment} from '../environments/environment';
import {ModalModule} from 'ngx-bootstrap/modal';
import {ButtonsModule} from 'ngx-bootstrap/buttons';
import {TypeaheadModule} from 'ngx-bootstrap/typeahead';
import {NgToggleModule} from '@nth-cloud/ng-toggle';
import {TooltipModule} from 'ngx-bootstrap/tooltip';
import {PortailComponent} from './portail/portail.component';
import {ErrorPageComponent} from './error-page/error-page.component';
import {Ability, AbilityClass, InferSubjects, PureAbility} from '@casl/ability';
import {AbilityModule} from '@casl/angular';
import {authConfig} from './config/auth.config';
import '@angular/common/locales/global/fr';
import '@angular/common/locales/global/en';
import { AutoTroubleshootComponent } from './auto-troubleshoot/auto-troubleshoot.component';
import { MemberPasswordEditComponent } from './member-password-edit/member-password-edit.component';

type Actions = 'manage' | 'create' | 'read' | 'update' | 'delete';
type Subjects = InferSubjects<Member> | InferSubjects<Transaction> | InferSubjects<Device> | InferSubjects<Account> | InferSubjects<Room> | InferSubjects<Port> | InferSubjects<ModelSwitch> | "all";

export type AppAbility = Ability<[Actions, Subjects]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

function load(oAuthService: OAuthService): Configuration {
  let params: ConfigurationParameters = 
  {
    basePath: environment.API_BASE_PATH,
    accessToken: oAuthService.getAccessToken() || "",
    apiKeys: {}
  };
  return new Configuration(params);
}

@NgModule({
  declarations: [
    AppComponent,
    GlobalSearchComponent,
    NavbarComponent,
    PortailComponent,
    ErrorPageComponent,
    AutoTroubleshootComponent,
    MemberPasswordEditComponent
  ],
  imports: [
    FontAwesomeModule,
    BrowserModule,
    AppRoutingModule,
    ApiModule,
    ReactiveFormsModule,
    FormsModule,
    BrowserAnimationsModule,
    OAuthModule.forRoot(),
    BsDropdownModule.forRoot(),
    HttpClientModule,
    ModalModule.forRoot(),
    ButtonsModule.forRoot(),
    TypeaheadModule.forRoot(),
    NgToggleModule,
    TooltipModule.forRoot(),
    AbilityModule,
  ],
  providers: [
    AppComponent,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: NotifInterceptor,
      multi: true
    },
    {provide: OAuthStorage, useFactory: (): OAuthStorage => localStorage},
    {provide: AuthConfig, useValue: authConfig},
    {
      provide: AppAbility, useValue: new AppAbility()
    },
    {provide: PureAbility, useExisting: AppAbility},
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
