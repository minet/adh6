import {Component, OnInit} from "@angular/core";
import {AsyncPipe, CommonModule} from "@angular/common";
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {finalize, map, Observable, shareReplay, switchMap} from "rxjs";
import {ActivatedRoute, RouterModule} from "@angular/router";
import {
  AbstractPort,
  AbstractSwitch,
  BulkOperationResult,
  PingRequest,
  PingResult,
  PortService,
  SwitchService,
  DiscoveredPort,
} from "../../api";
import {NotificationService} from "../../notification.service";
import {DialogService} from "../../ui/dialog.service";
import {ModalComponent} from "../../ui/modal.component";
import {loadAllPages} from "../../ui/entity-options";
import {missingDiscoveredPorts} from "../../port/port-discovery";

@Component({
  imports: [
    CommonModule,
    AsyncPipe,
    RouterModule,
    ReactiveFormsModule,
    ModalComponent,
  ],
  selector: "app-switch-admin",
  templateUrl: "./switch-admin.component.html",
  styles: `
    .discovered-ports {
      max-height: 300px;
      overflow-y: auto;
    }
  `,
})
export class SwitchAdminComponent implements OnInit {
  switchId = 0;
  switch$!: Observable<AbstractSwitch>;
  ports$!: Observable<AbstractPort[]>;

  applyingDescriptions = false;
  applyingVlans = false;
  syncingNames = false;
  pinging = false;
  discoveringNew = false;

  discoveredPorts: DiscoveredPort[] = [];
  selectedPorts = new Set<DiscoveredPort>();
  pingOpen = false;
  pingForm = new FormGroup({
    address: new FormControl("", {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.pattern(/^(\d{1,3}\.){3}\d{1,3}$/),
      ],
    }),
    count: new FormControl(5, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1), Validators.max(15)],
    }),
    size: new FormControl(100, {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.min(64),
        Validators.max(1500),
      ],
    }),
    timeoutMs: new FormControl(2000, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(100)],
    }),
  });

  constructor(
    private readonly route: ActivatedRoute,
    private readonly switchService: SwitchService,
    private readonly portService: PortService,
    private readonly notificationService: NotificationService,
    private readonly dialogService: DialogService,
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.switchId = +params["switch_id"];
      this.switch$ = this.switchService.switchIdGet(this.switchId);
      this.refreshPorts();
    });
  }

  refreshPorts(): void {
    this.ports$ = loadAllPages((limit, offset) =>
      this.portService.portGet(limit, offset, undefined, {
        switchObj: this.switchId,
      }),
    ).pipe(shareReplay(1));
  }

  isRoomError(port: AbstractPort): boolean {
    // Error if room ID is specified but room object is missing or invalid
    if (port.room === null || port.room === undefined) return false;
    return port.room <= 0 || !port.roomObj;
  }

  getRoomNumber(port: AbstractPort): number | string {
    if (port.room == null) return "-";
    if (this.isRoomError(port))
      return $localize`:@@common.invalid-id:ID invalide (${port.room}:INTERPOLATION:)`;
    return port.roomObj?.roomNumber ?? "...";
  }

  getRoomDescription(port: AbstractPort): string {
    if (port.room == null) return "-";
    if (this.isRoomError(port))
      return $localize`:@@switch.admin.load-error:Erreur de chargement`;
    return port.roomObj?.description ?? "...";
  }

  getRoomVlan(port: AbstractPort): number | string {
    if (port.room == null) return "-";
    if (this.isRoomError(port)) return "ERR";
    return port.roomObj?.vlan ?? "...";
  }

  syncPortNames(): void {
    this.syncingNames = true;
    this.switchService
      .switchIdSyncPortNamesPost(this.switchId)
      .pipe(finalize(() => (this.syncingNames = false)))
      .subscribe({
        next: (result: BulkOperationResult) => {
          this.notificationService.successNotification(
            $localize`:@@switch.admin.sync-names.result:Noms synchronisés : ${result.success ?? 0}:success: succès, ${result.failed ?? 0}:failed: échec(s)`,
          );
          this.refreshPorts();
        },
        error: (err: {status: number}) =>
          this.notificationService.errorNotification(err.status),
      });
  }

  discoverNewPorts(): void {
    if (this.discoveringNew) return;
    this.discoveringNew = true;
    loadAllPages((limit, offset) =>
      this.portService.portGet(limit, offset, undefined, {
        switchObj: this.switchId,
      }),
    )
      .pipe(
        switchMap((existingPorts) =>
          this.switchService
            .switchIdDiscoverPortsGet(this.switchId)
            .pipe(
              map((discovered) =>
                missingDiscoveredPorts(existingPorts, discovered),
              ),
            ),
        ),
        finalize(() => (this.discoveringNew = false)),
      )
      .subscribe({
        next: (newPorts) => {
          if (newPorts.length === 0) {
            void this.dialogService.alert({
              title: $localize`:@@switch.admin.no-new-ports:Aucun nouveau port`,
              text: $localize`:@@switch.admin.no-new-ports.desc:Tous les ports découverts sont déjà dans la base de données.`,
            });
            return;
          }
          this.discoveredPorts = newPorts;
          this.selectedPorts = new Set(newPorts);
        },
        error: (err: {status: number}) =>
          this.notificationService.errorNotification(err.status),
      });
  }

  togglePort(port: DiscoveredPort): void {
    if (!this.selectedPorts.delete(port)) {
      this.selectedPorts.add(port);
    }
  }

  toggleAllPorts(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectedPorts = new Set(checked ? this.discoveredPorts : []);
  }

  closeDiscovery(): void {
    this.discoveredPorts = [];
    this.selectedPorts.clear();
  }

  addDiscoveredPorts(): void {
    const portsToAdd: AbstractPort[] = this.discoveredPorts
      .filter((p) => this.selectedPorts.has(p))
      .map((p) => ({
        switchObj: this.switchId,
        portNumber: p.portNumber,
        oid: p.oid,
        room: undefined,
      }));
    this.closeDiscovery();
    if (portsToAdd.length === 0) {
      return;
    }

    this.portService.portBulkPost(portsToAdd).subscribe({
      next: (res) => {
        this.notificationService.successNotification(
          $localize`:@@switch.admin.ports-added:${res.success}:count: ports ajoutés.`,
        );
        this.refreshPorts();
      },
      error: (err: {status: number}) =>
        this.notificationService.errorNotification(err.status),
    });
  }

  applyDescriptions(): void {
    this.applyingDescriptions = true;
    this.switchService
      .switchIdApplyDescriptionsPost(this.switchId)
      .pipe(finalize(() => (this.applyingDescriptions = false)))
      .subscribe({
        next: (result: BulkOperationResult) =>
          this.notificationService.successNotification(
            $localize`:@@switch.admin.apply-descriptions.result:Descriptions appliquées : ${result.success ?? 0}:success: succès, ${result.failed ?? 0}:failed: échec(s)`,
          ),
        error: (err: {status: number}) =>
          this.notificationService.errorNotification(err.status),
      });
  }

  applyVlans(): void {
    void this.dialogService
      .prompt({
        title: $localize`:@@switch.admin.vlan.prompt:Entrer le numéro de VLAN`,
        label: $localize`:@@room.form.vlan:Numéro de VLAN`,
        type: "number",
        placeholder: $localize`:@@room.form.vlan.placeholder:ex : 42`,
        confirmText: $localize`:@@common.apply:Appliquer`,
        validate: (value) => {
          const n = Number(value);
          return value && Number.isInteger(n) && n >= 1 && n <= 4094
            ? null
            : $localize`:@@vlan.invalid:Entrer un numéro de VLAN valide (1–4094)`;
        },
      })
      .then((value) => {
        if (value === null) return;
        this.applyingVlans = true;
        this.switchService
          .switchIdApplyVlansPost(this.switchId, Number(value))
          .pipe(finalize(() => (this.applyingVlans = false)))
          .subscribe({
            next: (res: BulkOperationResult) =>
              this.notificationService.successNotification(
                $localize`:@@switch.admin.apply-vlans.result:VLANs appliqués : ${res.success ?? 0}:success: succès, ${res.failed ?? 0}:failed: échec(s)`,
              ),
            error: (err: {status: number}) =>
              this.notificationService.errorNotification(err.status),
          });
      });
  }

  openPing(): void {
    this.pingForm.reset();
    this.pingOpen = true;
  }

  pingSwitch(): void {
    if (this.pingForm.invalid) {
      this.pingForm.markAllAsTouched();
      return;
    }
    const req: PingRequest = this.pingForm.getRawValue();
    this.pingOpen = false;
    this.pinging = true;
    this.switchService
      .switchIdPingPost(this.switchId, req)
      .pipe(finalize(() => (this.pinging = false)))
      .subscribe({
        next: (res: PingResult) => {
          const received = res.received ?? 0;
          const pct = res.sent ? Math.round((received / res.sent) * 100) : 0;
          const rttLine =
            received > 0
              ? `\nRTT min/avg/max : ${res.minRtt}/${res.avgRtt}/${res.maxRtt} ms`
              : "";
          void this.dialogService.alert({
            title: $localize`:@@switch.admin.ping.result:Résultat du ping`,
            text:
              $localize`:@@switch.admin.ping.result.desc:Envoyés : ${res.sent ?? 0}:sent: ; Reçus : ${received}:received: (${pct}:pct: %)` +
              rttLine,
          });
        },
        error: (err: {status: number}) =>
          this.notificationService.errorNotification(err.status),
      });
  }
}
