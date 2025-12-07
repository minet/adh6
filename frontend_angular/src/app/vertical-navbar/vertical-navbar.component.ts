import {Component} from "@angular/core";
import {AsyncPipe} from "@angular/common";
import {RouterModule} from "@angular/router";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {AblePipe} from "@casl/angular";

@Component({
  imports: [AsyncPipe, RouterModule, AblePipe],
  selector: "app-vertical-navbar",
  templateUrl: "./vertical-navbar.component.html",
})
export class VerticalNavbarComponent {
  constructor(public oidcSecurityService: OidcSecurityService) {}
}
