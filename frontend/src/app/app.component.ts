import {animate, query, style, transition, trigger} from "@angular/animations";
import {Component} from "@angular/core";
import {RouterOutlet} from "@angular/router";
import {NavbarComponent} from "./navbar/navbar.component";
import {VerticalNavbarComponent} from "./vertical-navbar/vertical-navbar.component";
import {FooterComponent} from "./footer/footer.component";
import {AblePipe} from "@casl/angular";

export const fadeAnimation = trigger("fadeAnimation", [
  transition("* => *", [
    query(
      ":enter",
      [style({opacity: 0, position: "absolute", width: "100%", left: 0})],
      {
        optional: true,
      },
    ),
    query(
      ":leave",
      [
        style({opacity: 1}),
        animate(
          "0.15s",
          style({opacity: 0, position: "absolute", width: "100%", left: 0}),
        ),
      ],
      {optional: true},
    ),
    query(
      ":enter",
      [
        style({opacity: 0}),
        animate(
          "0.15s",
          style({opacity: 1, position: "absolute", width: "100%", left: 0}),
        ),
      ],
      {optional: true},
    ),
  ]),
]);

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
  animations: [fadeAnimation],
})
export class AppComponent {
  prepareRoute(outlet: RouterOutlet): string | undefined {
    return outlet?.activatedRouteData?.animation as string | undefined;
  }
}
