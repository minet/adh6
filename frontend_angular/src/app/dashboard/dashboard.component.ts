import {Component, OnInit} from '@angular/core';
import {OAuthService} from 'angular-oauth2-oidc';
import {Member, MemberService, MemberStatus, MiscService} from '../api';
import {LINKS_LIST, localize_link} from '../config/links.config';
import { LOCALE_ID, Inject } from '@angular/core';
import {AppConstantsService} from '../app-constants.service';
import {Observable, timer} from 'rxjs';
import {switchMap} from 'rxjs/operators';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  LINKS_LIST = LINKS_LIST;
  localize_link = localize_link;

  date = new Date();
  isDepartureDateFuture = false;
  isAssociationMode = false;
  member$: Observable<Member> = this.appConstantsService.getCurrentMember();
  stats$: Observable<any>;

  constructor(private oauthService: OAuthService,
              private appConstantsService: AppConstantsService,
              private memberService: MemberService,
              private statsService: MiscService,
              @Inject(LOCALE_ID) public locale: string) {
  }

  ngOnInit() {
    this.member$.subscribe(member => {
      this.isDepartureDateFuture = new Date() < new Date(member.departureDate);
      this.isAssociationMode = new Date() < new Date(member.associationMode);
    });
    this.stats$ = timer(0, 30 * 1000).pipe(
          switchMap(() => this.statsService.stats()
        ));
  }

  public get name() {
    const claims: any = this.oauthService.getIdentityClaims();
    if (!claims) { return null; }
    return claims.attributes.displayName;
  }
}
