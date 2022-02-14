import {AfterViewInit, Component, OnInit, ViewChild} from '@angular/core';
import {OAuthService} from 'angular-oauth2-oidc';
import {Configuration, Member} from '../api';
import {localize_link} from '../config/links.config';
import { LOCALE_ID, Inject } from '@angular/core';
import {AppConstantsService} from '../app-constants.service';
import {Observable} from 'rxjs';
import { ListComponent } from '../member-device/list/list.component';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  @ViewChild(ListComponent) wiredList:ListComponent;
  @ViewChild(ListComponent) wirelessList:ListComponent;

  localize_link = localize_link;

  date = new Date();
  isDepartureDateFuture = false;
  isAssociationMode = false;
  member$: Observable<Member> = this.appConstantsService.getCurrentMember();

  constructor(
    private oauthService: OAuthService,
    private appConstantsService: AppConstantsService,
    @Inject(LOCALE_ID) public locale: string
  ) { }

  ngOnInit() {
    this.member$.subscribe(member => {
      this.isDepartureDateFuture = new Date() < new Date(member.departureDate);
      this.isAssociationMode = new Date() < new Date(member.associationMode);
    });
  }

  public get name() {
    const claims: any = this.oauthService.getIdentityClaims();
    if (!claims) { return null; }
    if (!claims.attributes) { return null; }
    return claims.attributes.displayName;
  }
}
