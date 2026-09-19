import {Component, inject} from "@angular/core";
import {RouterModule} from "@angular/router";
import {AblePipe} from "@casl/angular";
import {AuthService} from "../auth/auth.service";

@Component({
  imports: [RouterModule, AblePipe],
  selector: "app-vertical-navbar",
  templateUrl: "./vertical-navbar.component.html",
})
export class VerticalNavbarComponent {
  protected readonly auth = inject(AuthService);
}
