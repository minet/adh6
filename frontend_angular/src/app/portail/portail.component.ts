import { Component } from '@angular/core';
import { OidcSecurityService } from 'angular-auth-oidc-client';

@Component({
  standalone: true,
  selector: 'app-portail',
  styles: ['img {height: 130px;}'],
  templateUrl: './portail.component.html'
})
export class PortailComponent {
  constructor(public oidcSecurityService: OidcSecurityService) { }
}
