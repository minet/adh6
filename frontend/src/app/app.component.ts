import {Component} from "@angular/core";
import {RouterOutlet} from "@angular/router";
import {NavbarComponent} from "./navbar/navbar.component";
import {VerticalNavbarComponent} from "./vertical-navbar/vertical-navbar.component";
import {FooterComponent} from "./footer/footer.component";
import {AblePipe} from "@casl/angular";
import {ToastsComponent} from "./ui/toasts.component";
import {DialogComponent} from "./ui/dialog.component";

@Component({
  imports: [
    RouterOutlet,
    NavbarComponent,
    VerticalNavbarComponent,
    FooterComponent,
    AblePipe,
    ToastsComponent,
    DialogComponent,
  ],
  selector: "app-root",
  templateUrl: "./app.component.html",
})
export class AppComponent {}
