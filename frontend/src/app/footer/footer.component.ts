import {Component, inject} from "@angular/core";
import {ThemeService} from "../theme.service";

@Component({
  selector: "app-footer",
  templateUrl: "./footer.component.html",
})
export class FooterComponent {
  protected readonly theme = inject(ThemeService);
}
