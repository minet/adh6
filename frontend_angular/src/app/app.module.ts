import {BrowserModule} from "@angular/platform-browser";
import {NgModule} from "@angular/core";
import {AppRoutingModule} from "./app-routing.module";
import {ApiModule, Configuration} from "./api";
import {CommonModule} from "@angular/common";
import {
  HTTP_INTERCEPTORS,
  provideHttpClient,
  withInterceptorsFromDi,
} from "@angular/common/http";
import {NotifInterceptor} from "./http-interceptor/notif-interceptor";
import {AuthTokenInterceptor} from "./http-interceptor/auth-token-interceptor";
import {environment} from "../environments/environment";
import {ReactiveFormsModule} from "@angular/forms";
import {Ability, AbilityClass, PureAbility} from "@casl/ability";
import {AblePipe} from "@casl/angular";
import "@angular/common/locales/global/fr";
import "@angular/common/locales/global/en";
import {AuthConfigModule} from "./auth.module";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";

type Actions = "manage" | "free";

export type AppAbility = Ability<[Actions, undefined]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

function load(): Configuration {
  const params = {
    basePath: environment.API_BASE_PATH,
  };
  return new Configuration(params);
}

@NgModule({
  declarations: [],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    CommonModule,
    AblePipe,
    ReactiveFormsModule,
    ApiModule,
    AuthConfigModule,
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: NotifInterceptor,
      multi: true,
    },
    {provide: HTTP_INTERCEPTORS, useClass: AuthTokenInterceptor, multi: true},
    {
      provide: AppAbility,
      useValue: new AppAbility(),
    },
    {provide: PureAbility, useExisting: AppAbility},
    {
      provide: Configuration,
      useFactory: load,
      multi: false,
    },
    provideHttpClient(withInterceptorsFromDi()),
  ],
})
export class AppModule {}
