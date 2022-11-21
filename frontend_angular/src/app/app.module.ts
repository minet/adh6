import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { ApiModule, Configuration } from './api';
import { NavbarComponent } from './navbar/navbar.component';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { NotifInterceptor } from './http-interceptor/notif-interceptor';
import { environment } from '../environments/environment';
import { Ability, AbilityClass, PureAbility } from '@casl/ability';
import { AbilityModule } from '@casl/angular';
import '@angular/common/locales/global/fr';
import '@angular/common/locales/global/en';
import { FooterComponent } from './footer/footer.component';
import { VerticalNavbarComponent } from './vertical-navbar/vertical-navbar.component';
import { AuthConfigModule } from './auth.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

type Actions = 'manage' | 'free';

export type AppAbility = Ability<[Actions, undefined]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

function load(): Configuration {
  let params =
  {
    basePath: environment.API_BASE_PATH,
  };
  return new Configuration(params);
}

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    FooterComponent,
    VerticalNavbarComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    AbilityModule,
    ApiModule,
    AuthConfigModule
  ],
  providers: [
    AppComponent,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: NotifInterceptor,
      multi: true
    },
    {
      provide: AppAbility, useValue: new AppAbility()
    },
    { provide: PureAbility, useExisting: AppAbility },
    {
      provide: Configuration,
      useFactory: load,
      multi: false
    },
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
