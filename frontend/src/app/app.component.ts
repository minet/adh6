import {Component} from "@angular/core";
import {RouterOutlet} from "@angular/router";
import {NavbarComponent} from "./navbar/navbar.component";
import {VerticalNavbarComponent} from "./vertical-navbar/vertical-navbar.component";
import {FooterComponent} from "./footer/footer.component";
import {AblePipe} from "@casl/angular";

@Component({
  standalone: true,
  imports: [
    RouterOutlet,
    NavbarComponent,
    VerticalNavbarComponent,
    FooterComponent,
    AblePipe,
  ],
  selector: "app-root",
  templateUrl: "./app.component.html",
})
export class AppComponent {}
