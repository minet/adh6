import {animate, query, style, transition, trigger} from "@angular/animations";
import {Component} from "@angular/core";
import {Router, RouterOutlet} from "@angular/router";
import {Ability, AbilityBuilder} from "@casl/ability";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {Configuration, MiscService} from "./api";
import {NavbarComponent} from "./navbar/navbar.component";
import {VerticalNavbarComponent} from "./vertical-navbar/vertical-navbar.component";
import {FooterComponent} from "./footer/footer.component";
import {AblePipe} from "@casl/angular";

export const fadeAnimation = trigger("fadeAnimation", [
  transition("* => *", [
    query(
      ":enter",
      [style({opacity: 0, position: "absolute", width: "100%", left: 0})],
      {
        optional: true,
      },
    ),
    query(
      ":leave",
      [
        style({opacity: 1}),
        animate(
          "0.15s",
          style({opacity: 0, position: "absolute", width: "100%", left: 0}),
        ),
      ],
      {optional: true},
    ),
    query(
      ":enter",
      [
        style({opacity: 0}),
        animate(
          "0.15s",
          style({opacity: 1, position: "absolute", width: "100%", left: 0}),
        ),
      ],
      {optional: true},
    ),
  ]),
]);

@Component({
  standalone: true,
  imports: [
    RouterOutlet,
    NavbarComponent,
    VerticalNavbarComponent,
    FooterComponent,
    AblePipe,
  ],
  selector: "app-root",
  templateUrl: "./app.component.html",
  animations: [fadeAnimation],
})
export class AppComponent {
  constructor(
    public oidcSecurityService: OidcSecurityService,
    private readonly ability: Ability,
    private readonly miscService: MiscService,
    private readonly configurationAPI: Configuration,
    private readonly router: Router,
  ) {
    this.oidcSecurityService.checkAuth().subscribe({
      next: ({isAuthenticated, accessToken}) => {
        if (isAuthenticated) {
          this.configurationAPI.credentials["OAuth2"] = accessToken;
          this.miscService.profile().subscribe({
            next: (r) => {
              const {can, rules} = new AbilityBuilder(Ability);
              if (
                r.roles?.indexOf("admin:read") !== -1 &&
                r.roles?.indexOf("admin:write") !== -1
              ) {
                can("manage", "admin");
              }
              if (
                r.roles?.indexOf("admin:prod") !== -1 &&
                r.roles?.indexOf("admin:write") !== -1
              ) {
                can("manage", "prod");
              }
              if (r.roles?.indexOf("treasurer:write") !== -1) {
                can("free", "Membership");
              }
              if (
                r.roles?.indexOf("treasurer:read") !== -1 &&
                r.roles?.indexOf("treasurer:write") !== -1
              ) {
                can("manage", "treasury");
              }
              if (r.member?.id != null) {
                can("read", "Member", {id: r.member.id});
              }
              this.ability.update(rules);
            },
            error: (error) => {
              console.error("Error fetching user profile:", error);
            },
          });
        } else {
          void this.router.navigate(["/portail"]);
        }
      },
      error: (error) => {
        console.error("Error checking authentication:", error);
        void this.router.navigate(["/portail"]);
      },
    });
  }

  prepareRoute(outlet: RouterOutlet): string | undefined {
    return outlet?.activatedRouteData?.animation as string | undefined;
  }
}
