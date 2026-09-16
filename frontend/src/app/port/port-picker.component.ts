import {
  Component,
  DestroyRef,
  EventEmitter,
  inject,
  Input,
  OnInit,
  Output,
} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {HttpErrorResponse} from "@angular/common/http";
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {firstValueFrom} from "rxjs";
import {
  AbstractPort,
  DiscoveredPort,
  Port,
  PortService,
  SwitchService,
} from "../api";
import {NotificationService} from "../notification.service";
import {ComboboxComponent, ComboboxOption} from "../ui/combobox.component";
import {DialogService} from "../ui/dialog.service";
import {loadAllPages, loadSwitchOptions} from "../ui/entity-options";

import {missingDiscoveredPorts} from "./port-discovery";

@Component({
  selector: "app-port-picker",
  imports: [ReactiveFormsModule, ComboboxComponent],
  styles: `
    :host {
      display: block;
    }
    .field:not(:last-child) {
      margin-bottom: 1.25rem;
    }
    .button {
      height: auto;
      min-height: 2.5em;
      white-space: normal;
      text-align: left;
    }
  `,
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      @if (switchId === null) {
        <div class="field">
          <label class="label" for="port-picker-switch" i18n="@@common.switch"
            >Commutateur</label
          >
          <app-combobox
            inputId="port-picker-switch"
            formControlName="switchId"
            [inlineOptions]="true"
            [options]="switchOptions"
            [loading]="switchesLoading"
            [unavailable]="switchesUnavailable"
            label="Commutateur"
            i18n-label="@@common.switch" />
          @if (switchesUnavailable) {
            <p class="help is-danger" i18n="@@switch.select.load-error">
              Impossible de charger les commutateurs.
            </p>
            <button
              type="button"
              class="button is-small"
              (click)="loadSwitches()"
              i18n="@@common.retry">
              Réessayer
            </button>
          }
        </div>
      }
      @if (form.controls.switchId.value !== null) {
        <div class="field">
          <label
            class="label"
            for="port-picker-port"
            i18n="@@port.picker.select"
            >Port</label
          >
          <app-combobox
            inputId="port-picker-port"
            formControlName="portKey"
            [inlineOptions]="true"
            [options]="portOptions"
            [loading]="portsLoading"
            [unavailable]="portsUnavailable"
            label="Port"
            i18n-label="@@port.picker.select"
            placeholder="Sélectionner un port"
            i18n-placeholder="@@port.picker.placeholder" />
          @if (portsUnavailable) {
            <p class="help is-danger" i18n="@@port.picker.load-error">
              Impossible de charger les ports.
            </p>
            <button
              type="button"
              class="button is-small"
              (click)="loadPorts()"
              i18n="@@common.retry">
              Réessayer
            </button>
          } @else if (!portsLoading && portOptions.length === 0) {
            <p class="help" i18n="@@port.picker.empty">
              Aucun port disponible. Lancez une découverte SNMP pour rechercher
              les ports manquants.
            </p>
          }
        </div>
        <div class="field">
          <button
            type="button"
            class="button"
            [class.is-loading]="discovering"
            [disabled]="
              saving || discovering || portsLoading || portsUnavailable
            "
            (click)="discover()"
            i18n="@@port.picker.discover">
            Découvrir les ports manquants via SNMP
          </button>
          @if (discoveryError) {
            <p
              class="help is-danger"
              role="alert"
              i18n="@@port.picker.discovery-error">
              La découverte SNMP a échoué. Les ports enregistrés restent
              disponibles ; aucun port manquant ne peut être ajouté.
            </p>
          } @else if (discoveryComplete && discoveredPorts.length === 0) {
            <p
              class="help"
              role="status"
              i18n="@@switch.admin.no-new-ports.desc">
              Tous les ports découverts sont déjà dans la base de données.
            </p>
          }
        </div>
      }
      @if (errorMessage) {
        <p class="help is-danger mb-3" role="alert">{{ errorMessage }}</p>
      }
      <button
        type="submit"
        class="button is-success"
        [class.is-loading]="saving"
        [disabled]="
          form.invalid ||
          saving ||
          portsLoading ||
          portsUnavailable ||
          switchesLoading ||
          switchesUnavailable
        ">
        @if (roomId !== null) {
          <span i18n="@@port.picker.assign">Rattacher à la chambre</span>
        } @else {
          <span i18n="@@port.picker.create">Créer le port découvert</span>
        }
      </button>
    </form>
  `,
})
export class PortPickerComponent implements OnInit {
  @Input() switchId: number | null = null;
  @Input() roomId: number | null = null;
  @Output() saved = new EventEmitter<Port>();
  readonly form = new FormGroup({
    switchId: new FormControl<number | null>(null, Validators.required),
    portKey: new FormControl<string | null>(null, Validators.required),
  });
  switchOptions: ComboboxOption[] = [];
  portOptions: ComboboxOption[] = [];
  ports: AbstractPort[] = [];
  discoveredPorts: DiscoveredPort[] = [];
  switchesLoading = false;
  switchesUnavailable = false;
  portsLoading = false;
  portsUnavailable = false;
  discovering = false;
  discoveryError = false;
  discoveryComplete = false;
  saving = false;
  errorMessage = "";
  private generation = 0;
  private readonly destroyRef = inject(DestroyRef);
  private readonly portService = inject(PortService);
  private readonly switchService = inject(SwitchService);
  private readonly dialogs = inject(DialogService);
  private readonly notifications = inject(NotificationService);

  ngOnInit(): void {
    this.form.controls.switchId.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.loadPorts());
    if (this.switchId != null) {
      this.form.controls.switchId.setValue(this.switchId);
    } else {
      this.loadSwitches();
    }
  }

  loadSwitches(): void {
    this.switchesLoading = true;
    this.switchesUnavailable = false;
    loadSwitchOptions(this.switchService)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (options) => {
          this.switchOptions = options;
          this.switchesLoading = false;
        },
        error: () => {
          this.switchesUnavailable = true;
          this.switchesLoading = false;
        },
      });
  }

  loadPorts(): void {
    const generation = ++this.generation;
    const switchId = this.form.controls.switchId.value;
    this.ports = [];
    this.discoveredPorts = [];
    this.portOptions = [];
    this.form.controls.portKey.reset();
    this.portsUnavailable = false;
    this.discovering = false;
    this.discoveryError = false;
    this.discoveryComplete = false;
    this.errorMessage = "";
    this.portsLoading = switchId != null;
    if (switchId == null) return;
    loadAllPages((limit, offset) =>
      this.portService.portGet(limit, offset, undefined, {switchObj: switchId}),
    )
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (ports) => {
          if (generation !== this.generation) return;
          this.ports = ports;
          this.portsLoading = false;
          this.updateOptions();
        },
        error: () => {
          if (generation !== this.generation) return;
          this.portsLoading = false;
          this.portsUnavailable = true;
        },
      });
  }

  discover(): void {
    const switchId = this.form.controls.switchId.value;
    if (
      switchId == null ||
      this.saving ||
      this.discovering ||
      this.portsLoading ||
      this.portsUnavailable
    )
      return;
    const generation = this.generation;
    this.discovering = true;
    this.discoveryError = false;
    this.discoveryComplete = false;
    this.switchService
      .switchIdDiscoverPortsGet(switchId)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (discovered) => {
          if (generation !== this.generation) return;
          this.discoveredPorts = missingDiscoveredPorts(this.ports, discovered);
          this.discovering = false;
          this.discoveryComplete = true;
          this.updateOptions();
        },
        error: () => {
          if (generation !== this.generation) return;
          this.discovering = false;
          this.discoveryError = true;
          this.discoveredPorts = [];
          this.updateOptions();
        },
      });
  }

  private updateOptions(): void {
    this.portOptions = [
      ...(this.roomId == null
        ? []
        : this.ports
            .filter((port) => port.id != null && port.room !== this.roomId)
            .map((port) => ({
              value: `existing:${port.id}`,
              displayLabel: port.portNumber ?? undefined,
              description: `OID ${port.oid} · ${
                port.room == null
                  ? $localize`:@@port.picker.unassigned:Sans chambre`
                  : $localize`:@@port.picker.room:Chambre ${port.roomObj?.roomNumber ?? port.room}:roomNumber:`
              }`,
              label: `${port.portNumber} ; OID ${port.oid} ; ${
                port.room == null
                  ? $localize`:@@port.picker.unassigned:Sans chambre`
                  : $localize`:@@port.picker.room:Chambre ${port.roomObj?.roomNumber ?? port.room}:roomNumber:`
              }`,
            }))),
      ...this.discoveredPorts.map((port) => ({
        value: `discovered:${port.oid}`,
        displayLabel: port.portNumber,
        description: `OID ${port.oid} · ${$localize`:@@port.picker.new:Nouveau port découvert`}`,
        label: `${port.portNumber} — OID ${port.oid} — ${$localize`:@@port.picker.new:Nouveau port découvert`}`,
      })),
    ];
    if (
      !this.portOptions.some(
        (option) => option.value === this.form.controls.portKey.value,
      )
    )
      this.form.controls.portKey.reset();
  }

  async submit(): Promise<void> {
    if (
      this.form.invalid ||
      this.saving ||
      this.portsLoading ||
      this.portsUnavailable ||
      this.switchesLoading ||
      this.switchesUnavailable
    )
      return;
    const {switchId, portKey} = this.form.getRawValue();
    const roomId = this.roomId;
    const generation = this.generation;
    const existing = this.ports.find(
      (port) => portKey === `existing:${port.id}`,
    );
    const discovered = this.discoveredPorts.find(
      (port) => portKey === `discovered:${port.oid}`,
    );
    if (
      !this.portOptions.some((option) => option.value === portKey) ||
      switchId == null ||
      (!existing && !discovered) ||
      (existing && this.roomId == null)
    )
      return;
    this.saving = true;
    this.errorMessage = "";
    this.form.disable({emitEvent: false});
    try {
      if (existing?.room != null && existing.room !== this.roomId) {
        const currentRoom = existing.roomObj?.roomNumber ?? existing.room;
        const confirmed = await this.dialogs.confirm({
          title: $localize`:@@port.picker.transfer.title:Transférer le port`,
          text: $localize`:@@port.picker.transfer.confirm:Le port ${existing.portNumber}:portNumber: est affecté à la chambre ${currentRoom}:roomNumber:. Confirmer son transfert vers cette chambre ?`,
          confirmText: $localize`:@@port.picker.transfer.action:Transférer`,
        });
        if (!confirmed || this.destroyRef.destroyed) return;
      }
      if (
        this.destroyRef.destroyed ||
        this.roomId !== roomId ||
        this.generation !== generation
      )
        return;
      const request = existing
        ? this.portService.portIdRoomPatch(existing.id!, {
            room: roomId!,
            expectedRoom: existing.room ?? null,
          })
        : this.portService.portPost({
            switchObj: switchId,
            oid: discovered!.oid,
            portNumber: discovered!.portNumber,
            room: roomId,
          });
      const port = await firstValueFrom(
        request.pipe(takeUntilDestroyed(this.destroyRef)),
      );
      if (this.destroyRef.destroyed) return;
      this.notifications.successNotification(
        $localize`:@@room.details.port-added:Port ajouté`,
      );
      this.saved.emit(port);
      if (this.roomId != null) this.loadPorts();
    } catch (error) {
      if (this.destroyRef.destroyed) return;
      if (error instanceof HttpErrorResponse && error.status === 409) {
        this.loadPorts();
        this.errorMessage = $localize`:@@port.picker.conflict:Le port existe déjà ou son affectation a changé. La liste a été actualisée ; sélectionnez à nouveau le port.`;
      } else {
        this.errorMessage = $localize`:@@port.picker.save-error:Impossible d’ajouter le port. Vérifiez la connexion et réessayez.`;
      }
    } finally {
      this.saving = false;
      this.form.enable({emitEvent: false});
    }
  }
}
