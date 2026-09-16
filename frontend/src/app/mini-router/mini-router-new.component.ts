import {Component, inject} from "@angular/core";
import {Router} from "@angular/router";
import {MiniRouter} from "../api";
import {MiniRouterFormComponent} from "./mini-router-form.component";

@Component({
  selector: "app-mini-router-new",
  imports: [MiniRouterFormComponent],
  template: `
    <h2 class="title is-2" i18n="@@mini-router.new.title">
      Nouveau mini-routeur
    </h2>
    <app-mini-router-form (saved)="onSaved($event)" />
  `,
})
export class MiniRouterNewComponent {
  private readonly router = inject(Router);

  onSaved(miniRouter: MiniRouter): void {
    void this.router.navigate(["/mini-router/view", miniRouter.id]);
  }
}
