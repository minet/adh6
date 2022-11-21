import { animate, query, state, style, transition, trigger } from '@angular/animations';
import { Component } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { Ability, AbilityBuilder } from '@casl/ability';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { Configuration, MiscService } from './api';


export const fadeAnimation = trigger('fadeAnimation', [
  transition('* => *', [
    query(':enter', [style({ opacity: 0, position: 'absolute', width: '100%', left: 0 })], {
      optional: true,
    }),
    query(
      ':leave',
      [
        style({ opacity: 1 }),
        animate('0.15s', style({ opacity: 0, position: 'absolute', width: '100%', left: 0 })),
      ],
      { optional: true }
    ),
    query(
      ':enter',
      [
        style({ opacity: 0 }),
        animate('0.15s', style({ opacity: 1, position: 'absolute', width: '100%', left: 0 })),
      ],
      { optional: true }
    ),
  ]),
]);


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  animations: [fadeAnimation]
})
export class AppComponent {
  constructor(
    public oidcSecurityService: OidcSecurityService,
    private ability: Ability,
    private miscService: MiscService,
    private configurationAPI: Configuration,
    private router: Router
  ) {
    this.oidcSecurityService.checkAuth().subscribe(({ isAuthenticated, accessToken }) => {
      if (isAuthenticated) {
        this.configurationAPI.credentials["OAuth2"] = accessToken;
        this.miscService.profile().subscribe(r => {
          const { can, rules } = new AbilityBuilder(Ability);
          if (r.roles.indexOf("admin:read") !== -1 && r.roles.indexOf("admin:write") !== -1) {
            can('manage', 'admin');
          }
          if (r.roles.indexOf("admin:prod") !== -1 && r.roles.indexOf("admin:write") !== -1) {
            can('manage', 'prod');
          }
          if (r.roles.indexOf('treasurer:write') !== -1) {
            can('free', 'Membership');
          }
          if (r.roles.indexOf('treasurer:read') !== -1 && r.roles.indexOf('treasurer:write') !== -1) {
            can('manage', 'treasury');
          }
          can('read', 'Member', { id: r.member.id });
          this.ability.update(rules);
        })
      } else {
        this.router.navigate(["/portail"])
      }
    });
  }
  
  prepareRoute(outlet: RouterOutlet) {
    return outlet && outlet.activatedRouteData && outlet.activatedRouteData.animation;
  }
}
