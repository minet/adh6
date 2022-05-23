import { Component } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { Router } from '@angular/router';
import { SessionService } from '../session.service';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  public isMenuActive: boolean = false;

  constructor(
    private oauthService: OAuthService,
    private router: Router,
    private sessionService: SessionService
  ) { }

  logout() {
    this.oauthService.logOut();
    this.router.navigate(['/portail']);
  }

  isAuthenticated() {
    return this.sessionService.isAuthenticated();
  }
}
