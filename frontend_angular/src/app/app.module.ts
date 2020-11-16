import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {AppComponent} from './app.component';
import {FontAwesomeModule} from '@fortawesome/angular-fontawesome';
import {AppRoutingModule} from './app-routing.module';
import {DashboardComponent} from './dashboard/dashboard.component';
import {SwitchLocalComponent} from './switch-local/switch-local.component';
import {MemberListComponent} from './member-list/member-list.component';
import {MemberViewComponent} from './member-view/member-view.component';
import {ApiModule, BASE_PATH, Device, Member, Room, Transaction, Account} from './api';
import {RoomListComponent} from './room-list/room-list.component';
import {RoomDetailsComponent} from './room-details/room-details.component';
import {RoomEditComponent} from './room-edit/room-edit.component';
import {RoomNewComponent} from './room-new/room-new.component';
import {PortListComponent} from './port-list/port-list.component';
import {PortDetailsComponent} from './port-details/port-details.component';
import {PortNewComponent} from './port-new/port-new.component';
import {SwitchListComponent} from './switch-list/switch-list.component';
import {SwitchDetailsComponent} from './switch-details/switch-details.component';
import {SwitchEditComponent} from './switch-edit/switch-edit.component';
import {SwitchNewComponent} from './switch-new/switch-new.component';
import {DeviceListComponent} from './device-list/device-list.component';
import {MemberCreateOrEditComponent} from './member-create-or-edit/member-create-or-edit.component';
import {MacVendorComponent} from './mac-vendor/mac-vendor.component';
import {GlobalSearchComponent} from './global-search/global-search.component';
import {NavbarComponent} from './navbar/navbar.component';
import {NotificationAnimationType, SimpleNotificationsModule} from 'angular2-notifications';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {AuthConfig, OAuthModule, OAuthStorage} from 'angular-oauth2-oidc';
import {LoginComponent} from './login/login.component';
import {NgxPaginationModule} from 'ngx-pagination';
import {BsDropdownModule} from 'ngx-bootstrap/dropdown';
import {PaginationModule} from 'ngx-bootstrap/pagination';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {AuthInterceptor} from './http-interceptor/auth-interceptor';
import {NotifInterceptor} from './http-interceptor/notif-interceptor';
import {MemberPasswordEditComponent} from './member-password-edit/member-password-edit.component';
import {TreasuryComponent} from './treasury/treasury.component';
import {ClickOutsideDirective, TransactionNewComponent} from './transaction-new/transaction-new.component';
import {environment} from '../environments/environment';
import {AccountCreateComponent} from './account-create/account-create.component';
import {AccountViewComponent} from './account-view/account-view.component';
import {AccountEditComponent} from './account-edit/account-edit.component';
import {ProductListComponent} from './product-list/product-list.component';
import {ModalModule} from 'ngx-bootstrap/modal';
import {CustomPaginationComponent} from './custom-pagination.component';
import {TransactionListComponent} from './transaction-list/transaction-list.component';
import {ButtonsModule} from 'ngx-bootstrap/buttons';
import {ObjectFilterPipe} from './ObjectFilter.pipe';
import {MemberDeviceListComponent} from './member-device-list/member-device-list.component';
import {AccountListComponent} from './account-list/account-list.component';
import {TypeaheadModule} from 'ngx-bootstrap/typeahead';
import {AuthorizeComponent} from './authorize/authorize.component';
import {NgToggleModule} from '@nth-cloud/ng-toggle';
import {TooltipModule} from 'ngx-bootstrap/tooltip';
import {BackButtonDirective} from './back-button.directive';
import {PortailComponent} from './portail/portail.component';
import {PortailCotisantComponent} from './portail-cotisant/portail-cotisant.component';
import {InscriptionComponent} from './inscription/inscription.component';
import {CotisantRecotisationComponent} from './cotisant-recotisation/cotisant-recotisation.component';
import {PortailfoyerComponent} from './portailfoyer/portailfoyer.component';
import {ErrorPageComponent} from './error-page/error-page.component';
import {Ability, AbilityClass, detectSubjectType, InferSubjects, PureAbility} from '@casl/ability';
import {AbilityModule} from '@casl/angular';
import {authConfig} from './config/auth.config';
import { DeviceNewComponent } from './device-new/device-new.component'
import '@angular/common/locales/global/fr';
import '@angular/common/locales/global/en';
import { AutoTroubleshootComponent } from './auto-troubleshoot/auto-troubleshoot.component';
import {Ng9OdometerModule} from 'ng9-odometer';

export {ClickOutsideDirective} from './clickOutside.directive';

type Actions = 'manage' | 'create' | 'read' | 'update' | 'delete';
type Subjects = InferSubjects<Member> | InferSubjects<Transaction> | InferSubjects<Device> | InferSubjects<Account> | InferSubjects<Room> | 'all';

export type AppAbility = Ability<[Actions, Subjects]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

export function storageFactory(): OAuthStorage {
  return localStorage;
}

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    SwitchLocalComponent,
    MemberListComponent,
    MemberViewComponent,
    RoomListComponent,
    RoomDetailsComponent,
    RoomEditComponent,
    RoomNewComponent,
    PortListComponent,
    PortDetailsComponent,
    PortNewComponent,
    SwitchListComponent,
    SwitchDetailsComponent,
    SwitchEditComponent,
    SwitchNewComponent,
    DeviceListComponent,
    MemberCreateOrEditComponent,
    MemberCreateOrEditComponent,
    MacVendorComponent,
    GlobalSearchComponent,
    NavbarComponent,
    LoginComponent,
    MemberPasswordEditComponent,
    TreasuryComponent,
    AccountCreateComponent,
    TransactionNewComponent,
    AccountViewComponent,
    AccountEditComponent,
    ProductListComponent,
    ClickOutsideDirective,
    CustomPaginationComponent,
    TransactionListComponent,
    ObjectFilterPipe,
    MemberDeviceListComponent,
    AccountListComponent,
    AuthorizeComponent,
    BackButtonDirective,
    PortailComponent,
    PortailCotisantComponent,
    InscriptionComponent,
    CotisantRecotisationComponent,
    PortailfoyerComponent,
    ErrorPageComponent,
    DeviceNewComponent,
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
    NgxPaginationModule,
    PaginationModule.forRoot(),
    BsDropdownModule.forRoot(),
    HttpClientModule,
    ModalModule.forRoot(),
    ButtonsModule.forRoot(),
    TypeaheadModule.forRoot(),
    NgToggleModule,
    TooltipModule.forRoot(),
    AbilityModule,
    Ng9OdometerModule.forRoot()
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
      provide: AppAbility, useValue: new AppAbility(undefined, {
        detectSubjectType: function (subject) {

          if (subject && typeof subject === 'object' && subject.__typename) {
            return subject.__typename;
          }

          return detectSubjectType(subject);
        }
      })
    },
    {provide: PureAbility, useExisting: AppAbility},
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
