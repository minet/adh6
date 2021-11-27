import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {AppComponent} from './app.component';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {AppRoutingModule} from './app-routing.module';
import {ApiModule, BASE_PATH, Device, Member, Room, Port, ModelSwitch, Transaction, Account} from './api';
import {GlobalSearchComponent} from './global-search/global-search.component';
import {NavbarComponent} from './navbar/navbar.component';
import {NotificationAnimationType, SimpleNotificationsModule} from 'angular2-notifications';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {AuthConfig, OAuthModule, OAuthStorage} from 'angular-oauth2-oidc';
import {BsDropdownModule} from 'ngx-bootstrap/dropdown';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {AuthInterceptor} from './http-interceptor/auth-interceptor';
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
import { ClickOutsideDirective } from './clickOutside.directive';

export {ClickOutsideDirective} from './clickOutside.directive';

type Actions = 'manage' | 'create' | 'read' | 'update' | 'delete';
type Subjects = InferSubjects<Member> | InferSubjects<Transaction> | InferSubjects<Device> | InferSubjects<Account> | InferSubjects<Room> | InferSubjects<Port> | InferSubjects<ModelSwitch> | "all";

export type AppAbility = Ability<[Actions, Subjects]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

export function storageFactory(): OAuthStorage {
  return localStorage;
}

@NgModule({
  declarations: [
    AppComponent,
    GlobalSearchComponent,
    NavbarComponent,
    ClickOutsideDirective,
    PortailComponent,
    ErrorPageComponent,
    AutoTroubleshootComponent,
  ],
  imports: [
    FontAwesomeModule,
    BrowserModule,
    AppRoutingModule,
    ApiModule,
    ReactiveFormsModule,
    FormsModule,
    SimpleNotificationsModule.forRoot({
      timeOut: 3000,
      clickToClose: false,
      clickIconToClose: true,
      animate: NotificationAnimationType.Fade,
      showProgressBar: false,
    }),
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
      useClass: AuthInterceptor,
      multi: true
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: NotifInterceptor,
      multi: true
    },
    {provide: BASE_PATH, useValue: environment.API_BASE_PATH},
    {provide: OAuthStorage, useFactory: storageFactory},
    {provide: AuthConfig, useValue: authConfig},
    {
      provide: AppAbility, useValue: new AppAbility()
    },
    {provide: PureAbility, useExisting: AppAbility},
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
