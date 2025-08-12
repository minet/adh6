import {Component} from "@angular/core";
import {OidcSecurityService} from "angular-auth-oidc-client";

@Component({
  selector: "app-navbar",
  templateUrl: "./navbar.component.html",
  standalone: false,
})
export class NavbarComponent {
  public isMenuActive: boolean = false;
  constructor(public oidcSecurityService: OidcSecurityService) {}

  logout() {
    this.oidcSecurityService.logoffLocal();
    location.href = "/portail";
  }
}
