import { Component } from '@angular/core';
import { AppComponent } from '../app.component';
import { OAuthService } from 'angular-oauth2-oidc';
import { authConfig } from '../config/auth.config';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  public isMenuActive: boolean = false;

  constructor(
    private oauthService: OAuthService,
    private appComponent: AppComponent
  ) { }

  logout() {
    this.oauthService.logOut();
    window.location.href = authConfig.logoutUrl;
  }

  isAuthenticated() {
    return this.appComponent.isAuthenticated();
  }
}
