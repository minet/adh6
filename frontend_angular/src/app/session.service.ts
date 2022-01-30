import { Injectable } from '@angular/core';
import { Ability, AbilityBuilder } from '@casl/ability';
import { OAuthService } from 'angular-oauth2-oidc';
import { filter } from 'rxjs';
import { Configuration } from './api';
import { AppConstantsService } from './app-constants.service';

@Injectable({
  providedIn: 'root'
})
export class SessionService {

  constructor(
    private oauthService: OAuthService,
    private configurationAPI: Configuration,
    private ability: Ability,
    private appConstantsService: AppConstantsService,
  ) { }

  checkSession(): void {
    if (this.oauthService.hasValidAccessToken()) {
      this.oauthService.loadDiscoveryDocumentAndTryLogin().then(_ => {
        this.oauthService.loadUserProfile()
          .then(v => {
            const _info = v['info'];
            if (_info === undefined) return
            this.loadProfileAndSetupAbilities(_info['attributes'])
          });
      });
      return;
    }

    this.oauthService.events
      .pipe(filter(e => e.type === 'token_received'))
      .subscribe(event => {
        console.log(event)
        this.configurationAPI.accessToken = this.oauthService.getAccessToken();
        this.oauthService.loadUserProfile()
          .then(v => {
            const _info = v['info'];
            if (_info === undefined) return
            this.loadProfileAndSetupAbilities(_info['attributes'])
          });
      });
    this.oauthService.loadDiscoveryDocumentAndTryLogin();
  }

  loadProfileAndSetupAbilities(attributes): void {
    if (this.oauthService.hasValidAccessToken()) {
      if (attributes === undefined) return;

      const { can, rules } = new AbilityBuilder(Ability);
      if (attributes['memberOf']) {
        const roles: Array<string> = attributes['memberOf'];
        if (roles.indexOf("cn=adh6_admin,ou=groups,dc=minet,dc=net") !== -1) {
          can('manage', 'Member');
          can('manage', 'Device');
          can('manage', 'Room');
          can('manage', 'Port');
          can('manage', 'Switch');
          can('manage', 'search');
          can('manage', 'switch_local');
        }
        if (roles.indexOf('cn=adh6_treso,ou=groups,dc=minet,dc=net') !== -1) {
          can('manage', 'treasury');
          can('manage', 'Transaction');
        }
      }
      else {
        this.appConstantsService.getCurrentMember().subscribe(member => can('read', 'Member', { id: member.id }));
      }
      this.ability.update(rules);
      this.appConstantsService.getCurrentMember();
    }
  }
}
