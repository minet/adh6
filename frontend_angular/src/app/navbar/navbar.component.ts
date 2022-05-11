import { Component } from '@angular/core';
import { AppComponent } from '../app.component';
import { OAuthService } from 'angular-oauth2-oidc';


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
  }

  isAuthenticated() {
    return this.appComponent.isAuthenticated();
  }
}
