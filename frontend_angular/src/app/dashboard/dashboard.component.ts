import {Component, OnInit} from '@angular/core';
import {OAuthService} from 'angular-oauth2-oidc';
import {Member} from '../api';
import {LINKS_LIST, localize_link} from '../config/links.config';

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
  member: Member = JSON.parse(localStorage.getItem('admin_member'));
  constructor(private oauthService: OAuthService) {
  }

  ngOnInit() {
    this.isDepartureDateFuture = new Date() < new Date(this.member.departureDate);
    console.log(this.member.departureDate);
  }

  public get name() {
    const claims: any = this.oauthService.getIdentityClaims();
    if (!claims) { return null; }
    return claims.attributes.displayName;
  }
}
