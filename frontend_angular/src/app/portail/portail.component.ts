import { Component } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';

@Component({
  selector: 'app-portail',
  templateUrl: './portail.component.html',
  styleUrls: ['./portail.component.css']
})
export class PortailComponent {
  constructor(
    public oauthService: OAuthService
  ) { }

  public login() {
    this.oauthService.initCodeFlow();
  }
}
