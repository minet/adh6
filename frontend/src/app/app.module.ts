import {BrowserModule} from "@angular/platform-browser";
import {NgModule, inject, provideAppInitializer} from "@angular/core";
import {AppRoutingModule} from "./app-routing.module";
import {ApiModule, Configuration} from "./api";
import {CommonModule} from "@angular/common";
import {provideHttpClient, withInterceptors} from "@angular/common/http";
import {notifInterceptor} from "./http-interceptor/notif-interceptor";
import {provideAbility} from "./auth/ability";
import {authInterceptor} from "./auth/auth.interceptor";
import {AuthService} from "./auth/auth.service";
import {environment} from "../environments/environment";
import {ReactiveFormsModule} from "@angular/forms";
import {AblePipe} from "@casl/angular";
import "@angular/common/locales/global/fr";
import "@angular/common/locales/global/en";

function load(): Configuration {
  const params = {
    basePath: environment.API_BASE_PATH,
    withCredentials: true,
  };
  return new Configuration(params);
}

@NgModule({
  declarations: [],
  imports: [
    BrowserModule,
    AppRoutingModule,
    CommonModule,
    AblePipe,
    ReactiveFormsModule,
    ApiModule,
  ],
  providers: [
    provideAbility(),
    {
      provide: Configuration,
      useFactory: load,
      multi: false,
    },
    provideAppInitializer(() => inject(AuthService).initialize()),
    provideHttpClient(withInterceptors([notifInterceptor, authInterceptor])),
  ],
})
export class AppModule {}
