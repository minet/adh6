import { Component } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { SessionService } from './session.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(
    private sessionService: SessionService,
    public oauthService: OAuthService,
  ) {
    this.sessionService.checkSession();
  }
}
