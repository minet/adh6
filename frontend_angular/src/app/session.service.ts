import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Ability, AbilityBuilder } from '@casl/ability';
import { OAuthService } from 'angular-oauth2-oidc';
import { filter, map, Observable, shareReplay } from 'rxjs';
import { Configuration, Member, MiscService } from './api';

@Injectable({
  providedIn: 'root'
})
export class SessionService {
  private user$: Observable<Member>;

  constructor(
    private oauthService: OAuthService,
    private configurationAPI: Configuration,
    private ability: Ability,
    private router: Router,
    private miscService: MiscService
  ) { }

  public getUser(): Observable<Member> {
    if (!this.user$) {
      this.refreshUser();
    }
    return this.user$;
  }

  public checkSession(): void {
    this.oauthService.loadDiscoveryDocumentAndTryLogin();
    if (this.oauthService.hasValidAccessToken()) {
      this.refreshResponse();
      return;
    }

    this.oauthService.events
      .pipe(filter(e => e.type === 'token_received'))
      .subscribe(e => {
        console.log(e);
        this.refreshResponse(e["access_token"]);
      });
  }

  public logout(): void {
    this.oauthService.logOut();
    const { rules } = new AbilityBuilder(Ability);
    this.ability.update(rules);
  }

  get isAuthenticated(): boolean {
    return this.oauthService.hasValidAccessToken();
  }

  private refreshResponse(token?: string): void {
    this.configurationAPI.accessToken = (token) ? token : this.oauthService.getAccessToken();
    this.refreshRights();
  }

  private refreshUser(): void {
    this.user$ = this.miscService.profile().pipe(
      shareReplay(1),
      map(r => r.member)
    )
  }

  private refreshRights(): void {
    this.miscService.profile().subscribe(r => {
      const { can, rules } = new AbilityBuilder(Ability);
      if (r.roles.indexOf("admin:read") !== -1 && r.roles.indexOf("admin:write") !== -1) {
        can('manage', 'admin');
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
  }
}
