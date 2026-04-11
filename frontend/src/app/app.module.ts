import {BrowserModule} from "@angular/platform-browser";
import {APP_INITIALIZER, NgModule} from "@angular/core";
import {AppRoutingModule} from "./app-routing.module";
import {ApiModule, Configuration, MiscService} from "./api";
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
import {Ability, AbilityBuilder, AbilityClass, PureAbility} from "@casl/ability";
import {AblePipe} from "@casl/angular";
import "@angular/common/locales/global/fr";
import "@angular/common/locales/global/en";
import {AuthConfigModule} from "./auth.module";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {firstValueFrom} from "rxjs";
import {Router} from "@angular/router";

type Actions = "manage" | "free";
type Subjects = string;

export type AppAbility = Ability<[Actions, Subjects]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

function load(): Configuration {
  const params = {
    basePath: environment.API_BASE_PATH,
  };
  return new Configuration(params);
}

function initializeAuth(
  oidcSecurityService: OidcSecurityService,
  configurationAPI: Configuration,
  miscService: MiscService,
  ability: Ability,
  router: Router,
): () => Promise<void> {
  return async () => {
    const {isAuthenticated, accessToken} = await firstValueFrom(
      oidcSecurityService.checkAuth(),
    );
    if (isAuthenticated) {
      configurationAPI.credentials["OAuth2"] = accessToken;
      try {
        const profile = await firstValueFrom(miscService.profile());
        const {can, rules} = new AbilityBuilder(Ability);
        if (
          profile.roles?.indexOf("admin:read") !== -1 &&
          profile.roles?.indexOf("admin:write") !== -1
        ) {
          can("manage", "admin");
        }
        if (
          profile.roles?.indexOf("admin:prod") !== -1 &&
          profile.roles?.indexOf("admin:write") !== -1
        ) {
          can("manage", "prod");
        }
        if (profile.roles?.indexOf("treasurer:write") !== -1) {
          can("free", "Membership");
        }
        if (
          profile.roles?.indexOf("treasurer:read") !== -1 &&
          profile.roles?.indexOf("treasurer:write") !== -1
        ) {
          can("manage", "treasury");
        }
        if (profile.member?.id != null) {
          can("read", "Member", {id: profile.member.id});
        }
        ability.update(rules);
      } catch (error) {
        console.error("Error fetching user profile:", error);
      }
    } else {
      void router.navigate(["/portail"]);
    }
  };
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
    {
      provide: APP_INITIALIZER,
      useFactory: initializeAuth,
      deps: [OidcSecurityService, Configuration, MiscService, AppAbility, Router],
      multi: true,
    },
    provideHttpClient(withInterceptorsFromDi()),
  ],
})
export class AppModule {}
