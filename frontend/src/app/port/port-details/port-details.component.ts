import {Component, OnDestroy, OnInit} from "@angular/core";
import {finalize, map, Observable, of, shareReplay, Subscription} from "rxjs";
import {
  PortService,
  Room,
  RoomService,
  SwitchService,
  AbstractPort,
} from "../../api";
import {ActivatedRoute, Router, RouterModule} from "@angular/router";
import {
  ReactiveFormsModule,
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
} from "@angular/forms";
import {NotificationService} from "../../notification.service";
import {DialogService} from "../../ui/dialog.service";
import {CommonModule} from "@angular/common";

@Component({
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  selector: "app-port-details",
  templateUrl: "./port-details.component.html",
  styleUrl: "./port-details.component.scss",
})
export class PortDetailsComponent implements OnInit, OnDestroy {
  vlanForm!: UntypedFormGroup;
  port$!: Observable<AbstractPort>;
  portID!: number;
  switchID!: number;

  changeVlanVisible = false;
  selectedVlan = 1;

  portSpeed!: string;

  private sub?: Subscription;

  public auth!: boolean;
  public use!: string;
  public alias!: string;
  public vlan!: number;

  public room_number$!: Observable<number>;
  public switch_description$!: Observable<string>;
  public mab$!: Observable<boolean>;
  public miniRouter$!: Observable<boolean>;
  public auth$!: Observable<boolean>;
  public use$!: Observable<string>;
  public status$!: Observable<boolean>;
  public alias$!: Observable<string>;
  public vlan$!: Observable<number>;

  constructor(
    private readonly portService: PortService,
    private readonly roomService: RoomService,
    private readonly switchService: SwitchService,
    private readonly fb: UntypedFormBuilder,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
    private readonly dialogService: DialogService,
  ) {
    this.createForm();
  }

  createForm(): void {
    this.vlanForm = this.fb.group({
      vlanNumber: [
        1,
        [Validators.required, Validators.min(1), Validators.max(4096)],
      ],
    });
  }

  get newVlanNumber(): number {
    return this.vlanForm.value.vlanNumber as number;
  }

  getUse(state: string): string {
    return state == "authorized"
      ? $localize`:@@port.use.used:Le port est actuellement utilisé`
      : $localize`:@@port.use.unused:Le port n'est pas actuellement utilisé`;
  }
  getStatus(state: boolean): string {
    return state
      ? $localize`:@@port.status.open:OUVERT`
      : $localize`:@@port.status.closed:FERMÉ`;
  }
  getState(state: boolean): string {
    return state
      ? $localize`:@@port.state.enabled:ACTIVÉ`
      : $localize`:@@port.state.disabled:DÉSACTIVÉ`;
  }

  public toggleStatus(): void {
    this.status$ = this.portService.portIdStatePut(this.portID).pipe(
      finalize(() => {
        this.notificationService.successNotification(
          $localize`:@@port.status.updated:État du port modifié`,
        );
      }),
    );
  }

  public toggleMAB(): void {
    this.mab$ = this.portService.portIdMabPut(this.portID).pipe(
      finalize(() => {
        this.notificationService.successNotification(
          $localize`:@@port.mab.updated:MAB modifié`,
        );
      }),
    );
  }

  public toggleMiniRouter(currentValue: boolean): void {
    this.miniRouter$ = this.portService
      .portIdMiniRouterPut(this.portID, !currentValue)
      .pipe(
        finalize(() => {
          this.notificationService.successNotification(
            $localize`:@@port.mini-router.updated:Mini-Routeur modifié`,
          );
        }),
      );
  }

  public togglePubliclyAccessible(port: AbstractPort): void {
    const updated: AbstractPort = {
      ...port,
      publiclyAccessible: !port.publiclyAccessible,
    };
    this.portService
      .portIdPut(this.portID, updated)
      .pipe(
        finalize(() => {
          this.notificationService.successNotification(
            $localize`:@@port.public-access.updated:Accès public modifié`,
          );
        }),
      )
      .subscribe(() => {
        this.port$ = this.portService.portIdGet(this.portID).pipe(
          map((p) => {
            if (p.roomObj) {
              this.room_number$ = of(p.roomObj.roomNumber ?? 0);
            }
            if (p.switchObj) {
              this.switch_description$ = this.switchService
                .switchIdGet(p.switchObj, ["description"])
                .pipe(
                  shareReplay(1),
                  map((s) => s.description ?? ""),
                );
            }
            return p;
          }),
        );
      });
  }

  public toggleAuth(currentValue: boolean): void {
    if (currentValue) {
      void this.dialogService
        .prompt({
          title: $localize`:@@port.vlan.prompt:Entrer le VLAN`,
          label: "VLAN",
          type: "number",
          placeholder: $localize`:@@port.vlan.prompt:Entrer le VLAN`,
          validate: (value) => {
            const n = Number(value);
            return Number.isInteger(n) && n >= 1 && n <= 4094
              ? null
              : $localize`:@@vlan.invalid:Entrer un numéro de VLAN valide (1–4094)`;
          },
        })
        .then((value) => {
          if (value === null) return;
          const vlan = Number(value);
          this.auth$ = this.portService.portIdAuthPut(this.portID).pipe(
            finalize(() => {
              this.notificationService.successNotification(
                $localize`:@@port.auth.updated:Authentification modifiée`,
              );
            }),
          );
          this.portService.portIdVlanPut(this.portID, vlan).subscribe(() => {
            this.notificationService.successNotification(
              $localize`:@@port.vlan.updated:VLAN modifié : ${vlan}:vlan:`,
            );
          });
          this.vlan$ = of(vlan);
        });
    } else {
      this.auth$ = this.portService.portIdAuthPut(this.portID).pipe(
        finalize(() => {
          this.notificationService.successNotification(
            $localize`:@@port.auth.updated:Authentification modifiée`,
          );
        }),
      );
      this.vlan$ = this.portService.vlanGet(this.portID);
    }
  }

  IfRoomExists(roomNumber: Room) {
    if (roomNumber == null) {
      this.notificationService.errorNotification(
        404,
        "No room found",
        "This port is not assigned to a room",
      );
    } else {
      void this.router.navigate(["/room/view", roomNumber.roomNumber]);
    }
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe((params) => {
      this.switchID = +params["switch_id"];
      this.portID = +params["port_id"];
      this.port$ = this.portService.portIdGet(this.portID).pipe(
        map((p) => {
          if (p.roomObj) {
            this.room_number$ = of(p.roomObj.roomNumber ?? 0);
          }
          if (p.switchObj) {
            this.switch_description$ = this.switchService
              .switchIdGet(p.switchObj, ["description"])
              .pipe(
                shareReplay(1),
                map((s) => s.description ?? ""),
              );
          }
          return p;
        }),
      );
    });

    this.refreshInfo();
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }

  refreshInfo(): void {
    this.auth$ = this.portService.authGet(this.portID);
    this.status$ = this.portService.stateGet(this.portID);
    this.mab$ = this.portService.mabGet(this.portID);
    this.miniRouter$ = this.portService.miniRouterGet(this.portID);
    this.use$ = this.portService.useGet(this.portID);
    this.vlan$ = this.portService.vlanGet(this.portID);
    this.alias$ = this.portService.aliasGet(this.portID);
  }
}
