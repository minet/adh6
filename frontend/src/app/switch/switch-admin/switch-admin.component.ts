import {Component, OnInit} from "@angular/core";
import {AsyncPipe, CommonModule} from "@angular/common";
import {finalize, forkJoin, Observable, shareReplay, tap, take} from "rxjs";
import {ActivatedRoute, RouterModule} from "@angular/router";
import {
  AbstractPort,
  AbstractRoom,
  AbstractSwitch,
  BulkOperationResult,
  PingRequest,
  PingResult,
  PortService,
  RoomService,
  SwitchService,
  DiscoveredPort,
} from "../../api";
import {NotificationService} from "../../notification.service";
import Swal from "sweetalert2";

@Component({
  imports: [CommonModule, AsyncPipe, RouterModule],
  selector: "app-switch-admin",
  templateUrl: "./switch-admin.component.html",
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

  roomCache = new Map<number, AbstractRoom>();

  constructor(
    private readonly route: ActivatedRoute,
    private readonly switchService: SwitchService,
    private readonly portService: PortService,
    private readonly roomService: RoomService,
    private readonly notificationService: NotificationService,
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.switchId = +params["switch_id"];
      this.switch$ = this.switchService.switchIdGet(this.switchId);
      this.refreshPorts();
    });
  }

  refreshPorts(): void {
    this.ports$ = this.portService
      .portGet(500, 0, undefined, {switchObj: this.switchId})
      .pipe(
        tap((ports) => this.loadRooms(ports)),
        shareReplay(1),
      );
  }

  private loadRooms(ports: AbstractPort[]): void {
    const roomIds = [
      ...new Set(
        ports
          .filter((p) => p.room != null)
          .map((p) => p.room as number),
      ),
    ];
    if (roomIds.length === 0) return;
    forkJoin(
      roomIds.map((id) => this.roomService.roomIdGet(id).pipe(shareReplay(1))),
    ).subscribe((rooms) => {
      rooms.forEach((room) => {
        if (room.id != null) {
          this.roomCache.set(room.id, room);
        }
      });
    });
  }

  getRoomNumber(roomId: number | null | undefined): number | string {
    if (roomId == null) return "-";
    return this.roomCache.get(roomId)?.roomNumber ?? "...";
  }

  getRoomDescription(roomId: number | null | undefined): string {
    if (roomId == null) return "-";
    return this.roomCache.get(roomId)?.description ?? "...";
  }

  getRoomVlan(roomId: number | null | undefined): number | string {
    if (roomId == null) return "-";
    return this.roomCache.get(roomId)?.vlan ?? "...";
  }

  syncPortNames(): void {
    this.syncingNames = true;
    this.switchService.switchIdSyncPortNamesPost(this.switchId)
      .pipe(finalize(() => this.syncingNames = false))
      .subscribe({
        next: (result: BulkOperationResult) => {
          this.notificationService.successNotification(
            `Noms synchronisés : ${result.success ?? 0} succès, ${result.failed ?? 0} échec(s)`
          );
          this.refreshPorts();
        },
        error: (err: {status: number}) => this.notificationService.errorNotification(err.status)
      });
  }

  discoverNewPorts(): void {
    this.discoveringNew = true;
    // 1. Get existing ports to know what to filter
    this.ports$.pipe(take(1)).subscribe(existingPorts => {
      const existingOids = new Set(existingPorts.map(p => p.oid));

      // 2. Discover via SNMP
      this.switchService.switchIdDiscoverPortsGet(this.switchId)
        .pipe(finalize(() => this.discoveringNew = false))
        .subscribe({
          next: (discovered) => {
            const newPorts = discovered.filter(p => p.oid && !existingOids.has(p.oid));
            
            if (newPorts.length === 0) {
              void Swal.fire("Aucun nouveau port", "Tous les ports découverts sont déjà dans la base de données.", "info");
              return;
            }

            this.showDiscoveryModal(newPorts);
          },
          error: (err: {status: number}) => this.notificationService.errorNotification(err.status)
        });
    });
  }

  private showDiscoveryModal(newPorts: DiscoveredPort[]): void {
    const html = `
      <div class="table-container" style="max-height: 300px; overflow-y: auto; text-align: left;">
        <table class="table is-fullwidth is-narrow is-striped">
          <thead>
            <tr>
              <th><input type="checkbox" id="swal-toggle-all" checked></th>
              <th>Nom</th>
              <th>OID</th>
            </tr>
          </thead>
          <tbody>
            ${newPorts.map((p, i) => `
              <tr>
                <td><input type="checkbox" class="swal-port-cb" data-index="${i}" checked></td>
                <td>${p.portNumber}</td>
                <td>${p.oid}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;

    void Swal.fire({
      title: "Nouveaux ports découverts",
      html: html,
      showCancelButton: true,
      confirmButtonText: "Ajouter la sélection",
      cancelButtonText: "Annuler",
      didOpen: () => {
        const toggleAll = document.getElementById("swal-toggle-all") as HTMLInputElement;
        const cbs = document.querySelectorAll(".swal-port-cb") as NodeListOf<HTMLInputElement>;
        toggleAll.addEventListener("change", () => {
          cbs.forEach(cb => cb.checked = toggleAll.checked);
        });
      },
      preConfirm: () => {
        const cbs = document.querySelectorAll(".swal-port-cb:checked") as NodeListOf<HTMLInputElement>;
        return Array.from(cbs).map(cb => {
          const idx = parseInt(cb.getAttribute("data-index")!, 10);
          return newPorts[idx];
        });
      }
    }).then(result => {
      if (result.isConfirmed && result.value && result.value.length > 0) {
        this.addDiscoveredPorts(result.value);
      }
    });
  }

  private addDiscoveredPorts(ports: DiscoveredPort[]): void {
    const portsToAdd: AbstractPort[] = ports.map(p => ({
      switchObj: this.switchId,
      portNumber: p.portNumber,
      oid: p.oid,
      room: undefined
    }));

    this.portService.portBulkPost(portsToAdd).subscribe({
      next: (res) => {
        this.notificationService.successNotification(`${res.success} ports ajoutés.`);
        this.refreshPorts();
      },
      error: (err: {status: number}) => this.notificationService.errorNotification(err.status)
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
            `Descriptions appliquées : ${result.success ?? 0} succès, ${result.failed ?? 0} échec(s)`,
          ),
        error: (err: {status: number}) =>
          this.notificationService.errorNotification(err.status),
      });
  }

  applyVlans(): void {
    void Swal.fire({
      title: "Entrer le numéro de VLAN",
      icon: "question",
      input: "number",
      inputLabel: "Numéro de VLAN",
      inputPlaceholder: "ex: 42",
      inputAttributes: {min: "1", max: "4094"},
      showCancelButton: true,
      confirmButtonText: "Appliquer",
      cancelButtonText: "Annuler",
      inputValidator: (value) => {
        const n = parseInt(value, 10);
        if (!value || isNaN(n) || n < 1 || n > 4094) {
          return "Entrer un numéro de VLAN valide (1–4094)";
        }
        return null;
      },
    }).then((result) => {
      if (!result.isConfirmed) return;
      const vlanNumber = parseInt(result.value as string, 10);
      this.applyingVlans = true;
      this.switchService
        .switchIdApplyVlansPost(this.switchId, vlanNumber)
        .pipe(finalize(() => (this.applyingVlans = false)))
        .subscribe({
          next: (res: BulkOperationResult) =>
            this.notificationService.successNotification(
              `VLANs appliqués : ${res.success ?? 0} succès, ${res.failed ?? 0} échec(s)`,
            ),
          error: (err: {status: number}) =>
            this.notificationService.errorNotification(err.status),
        });
    });
  }

  pingSwitch(): void {
    void Swal.fire({
      title: "Ping depuis le commutateur",
      icon: "question",
      html:
        '<div class="field"><label class="label">Adresse IP cible</label>' +
        '<input id="swal-ping-addr" class="input" type="text" placeholder="ex: 192.168.0.1"></div>' +
        '<div class="columns"><div class="column"><div class="field"><label class="label">Nombre de paquets (1–15)</label>' +
        '<input id="swal-ping-count" class="input" type="number" value="5" min="1" max="15"></div></div>' +
        '<div class="column"><div class="field"><label class="label">Taille (64–1500)</label>' +
        '<input id="swal-ping-size" class="input" type="number" value="100" min="64" max="1500"></div></div></div>' +
        '<div class="field"><label class="label">Délai d\'attente (ms)</label>' +
        '<input id="swal-ping-timeout" class="input" type="number" value="2000" min="100"></div>',
      showCancelButton: true,
      confirmButtonText: "Ping",
      cancelButtonText: "Annuler",
      focusConfirm: false,
      preConfirm: () => {
        const addr = (document.getElementById("swal-ping-addr") as HTMLInputElement).value.trim();
        const count = parseInt((document.getElementById("swal-ping-count") as HTMLInputElement).value, 10);
        const size = parseInt((document.getElementById("swal-ping-size") as HTMLInputElement).value, 10);
        const timeoutMs = parseInt((document.getElementById("swal-ping-timeout") as HTMLInputElement).value, 10);

        if (!addr) {
          Swal.showValidationMessage("L'adresse IP est requise");
          return false;
        }
        const ipv4 = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (!ipv4.test(addr)) {
          Swal.showValidationMessage("Adresse IPv4 invalide");
          return false;
        }
        if (isNaN(count) || count < 1 || count > 15) {
          Swal.showValidationMessage("Le nombre de paquets doit être entre 1 et 15");
          return false;
        }
        if (isNaN(size) || size < 64 || size > 1500) {
          Swal.showValidationMessage("La taille doit être entre 64 et 1500 octets");
          return false;
        }
        if (isNaN(timeoutMs) || timeoutMs < 100) {
          Swal.showValidationMessage("Le délai d'attente doit être au moins 100 ms");
          return false;
        }
        return {address: addr, count, size, timeoutMs};
      },
    }).then((result) => {
      if (!result.isConfirmed || !result.value) return;
      const req: PingRequest = {
        address: result.value.address as string,
        count: result.value.count as number,
        size: result.value.size as number,
        timeoutMs: result.value.timeoutMs as number,
      };
      this.pinging = true;
      this.switchService
        .switchIdPingPost(this.switchId, req)
        .pipe(finalize(() => (this.pinging = false)))
        .subscribe({
          next: (res: PingResult) => {
            const pct = res.sent ? Math.round(((res.received ?? 0) / res.sent) * 100) : 0;
            const rttLine =
              (res.received ?? 0) > 0
                ? `<br>RTT min/avg/max : ${res.minRtt}/${res.avgRtt}/${res.maxRtt} ms`
                : "";
            void Swal.fire({
              title: "Résultat du ping",
              icon: (res.received ?? 0) > 0 ? "success" : "warning",
              html: `Envoyés : ${res.sent ?? 0} — Reçus : ${res.received ?? 0} (${pct} %)${rttLine}`,
            });
          },
          error: (err: {status: number}) =>
            this.notificationService.errorNotification(err.status),
        });
    });
  }
}
