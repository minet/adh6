import {Component, inject} from "@angular/core";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {ThemeService} from "../theme.service";

@Component({
  standalone: true,
  selector: "app-portail",
  styles: ["img {height: 130px;}"],
  templateUrl: "./portail.component.html",
})
export class PortailComponent {
  protected readonly theme = inject(ThemeService);
  constructor(public oidcSecurityService: OidcSecurityService) {}
}
