import {Component, OnInit} from '@angular/core';
import {OAuthService} from 'angular-oauth2-oidc';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  constructor(private oauthService: OAuthService) {
  }

  ngOnInit() {
  }

  public get name() {
    const claims: any = this.oauthService.getIdentityClaims();
    if (!claims) { return null; }
    return claims.attributes.displayName;
  }
}
