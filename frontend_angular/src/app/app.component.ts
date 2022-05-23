import { Component } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { Router } from '@angular/router';
import { Configuration } from './api';
import { SessionService } from './session.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(
    private oauthService: OAuthService,
    private configurationAPI: Configuration,
    private sessionService: SessionService,
    private router: Router,
  ) {
    this.sessionService.checkSession();
    if (!this.isAuthenticated) {
      this.router.navigate(['/portail'])
    }
  }

  isAuthenticated() {
    return (this.oauthService.hasValidAccessToken()) && this.configurationAPI.accessToken != "";
  }
}
