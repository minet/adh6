import { Component } from '@angular/core';
import { OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
  selector: 'app-vertical-navbar',
  templateUrl: './vertical-navbar.component.html'
})
export class VerticalNavbarComponent {
  constructor(public oidcSecurityService: OidcSecurityService) { }
}
