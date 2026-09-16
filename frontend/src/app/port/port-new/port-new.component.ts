import {ActivatedRoute, Router} from "@angular/router";
import {Component, inject} from "@angular/core";
import {AsyncPipe} from "@angular/common";
import {map} from "rxjs";
import {Port} from "../../api";
import {PortPickerComponent} from "../port-picker.component";

@Component({
  selector: "app-port-new",
  imports: [AsyncPipe, PortPickerComponent],
  template: `
    <h1 class="title is-1" i18n="@@port.new.title">Création d'un port</h1>
    <p class="mb-4" i18n="@@port.new.discovery-help">
      Découvrez les ports du switch via SNMP, puis sélectionnez le port à créer.
      L’affectation à une chambre se fait depuis la fiche de la chambre.
    </p>
    @if (switchId$ | async; as switchId) {
      @for (id of [switchId]; track id) {
        <app-port-picker [switchId]="id" (saved)="onSaved($event)" />
      }
    }
  `,
})
export class PortNewComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  readonly switchId$ = this.route.params.pipe(
    map((params) => +params["switch_id"]),
  );

  onSaved(port: Port): void {
    void this.router.navigate(["/port", port.switchObj, port.id]);
  }
}
