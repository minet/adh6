import {Component} from "@angular/core";
import {AsyncPipe, CommonModule} from "@angular/common";
import {RouterModule} from "@angular/router";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {AblePipe} from "@casl/angular";

@Component({
  standalone: true,
  imports: [AsyncPipe, CommonModule, RouterModule, AblePipe],
  selector: "app-navbar",
  templateUrl: "./navbar.component.html",
})
export class NavbarComponent {
  public isMenuActive = false;
  constructor(public oidcSecurityService: OidcSecurityService) {}

  logout() {
    this.oidcSecurityService
      .logoff()
      .subscribe((result) => console.log(result));
  }
}
