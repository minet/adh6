import { Component, OnDestroy, OnInit } from '@angular/core';
import { finalize, map, Observable, of, shareReplay } from 'rxjs';
import { PortService, Room, RoomService, SwitchService, AbstractPort } from '../../api';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import Swal from 'sweetalert2';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-port-details',
  templateUrl: './port-details.component.html',
  styleUrls: ['./port-details.component.css']
})
export class PortDetailsComponent implements OnInit, OnDestroy {
  vlanForm: FormGroup;
  port$: Observable<AbstractPort>;
  portID: number;
  switchID: number;

  changeVlanVisible = false;
  selectedVlan: number = 1;

  portSpeed: string;

  private sub: any;

  public auth: boolean;
  public use: string;
  public alias: string;
  public vlan: number;

  public room_number$: Observable<number>;
  public switch_description$: Observable<string>;
  public mab$: Observable<boolean>;
  public auth$: Observable<boolean>;
  public use$: Observable<string>;
  public status$: Observable<boolean>;
  public alias$: Observable<string>;
  public vlan$: Observable<number>;

  constructor(
    private portService: PortService,
    private roomService: RoomService,
    private switchService: SwitchService,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private notificationService: NotificationService
  ) {
    this.createForm();
  }

  createForm(): void {
    this.vlanForm = this.fb.group({
      vlanNumber: [1, [Validators.required, Validators.min(1), Validators.max(4096)]]
    })
  }

  get newVlanNumber(): number {
    return this.vlanForm.value.vlanNumber as number;
  }

  getUse(state: string): string {
    return (state == "authorized") ? 'Le port est actuellement utilisé' : 'Le port n\'est pas actuellement utilisé';
  }
  getStatus(state: boolean): string {
    return (state) ? 'OUVERT' : 'FERMÉ';
  }
  getState(state: boolean): string {
    return (state) ? 'ACTIVÉ' : 'DÉSACTIVÉ';
  }
  getAction(state: boolean): string {
    return (state) ? 'ACTIVER' : 'DÉSACTIVER';
  }

  public toggleStatus(): void {
    this.status$ = this.portService.portIdStatePut(this.portID)
      .pipe(finalize(() => {
        this.notificationService.successNotification("État du port modifié");
      }));
  }

  public toggleMAB(): void {
    this.mab$ = this.portService.portIdMabPut(this.portID)
      .pipe(finalize(() => {
        this.notificationService.successNotification("MAB modifié");
      }));
  }

  public toggleAuth(currentValue: boolean): void {
    if (currentValue) {
      Swal.fire({
        title: 'Entrer le VLAN',
        icon: 'question',
        input: 'number',
        inputLabel: 'VLAN 1',
        inputPlaceholder: 'Entrer le VLAN',
        showCancelButton: true
      }).then((result) => {
        if (result.isConfirmed) {
          this.auth$ = this.portService.portIdAuthPut(this.portID)
            .pipe(finalize(() => {
              this.notificationService.successNotification("Authentification modifiée");
            }));
          this.portService.portIdVlanPut(result.value, this.portID)
            .subscribe(() => {
              this.notificationService.successNotification("VLAN modifié: " + result.value);
            });
          this.vlan$ = of(result.value);
          return;
        }
      });
    } else {
      this.auth$ = this.portService.portIdAuthPut(this.portID)
        .pipe(finalize(() => {
          this.notificationService.successNotification("Authentification modifiée");
        }));
      this.vlan$ = this.portService.vlanGet(this.portID);
    }
  }

  submitVLAN(vlan: number) {
    console.log(vlan)
  }

  IfRoomExists(roomNumber: Room) {
    console.log(roomNumber);
    if (roomNumber == null) {
      this.notificationService.errorNotification(
        404,
        "No room found",
        'This port is not assigned to a room'
      );
    } else {
      this.router.navigate(['/room/view', roomNumber.roomNumber]);
    }
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.switchID = +params['switch_id'];
      this.portID = +params['port_id'];
      this.port$ = this.portService.portIdGet(this.portID)
        .pipe(map(p => {
          if (p.room) {
            this.room_number$ = this.roomService.roomIdGet(p.room, ["roomNumber"]).pipe(shareReplay(1), map(r => r.roomNumber));
          }
          if (p.switchObj) {
            this.switch_description$ = this.switchService.switchIdGet(p.switchObj, ["description"]).pipe(shareReplay(1), map(s => s.description));
          }
          return p;
        }));
    });

    this.refreshInfo();
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  refreshInfo(): void {
    this.auth$ = this.portService.authGet(this.portID);
    this.status$ = this.portService.stateGet(this.portID);
    this.mab$ = this.portService.mabGet(this.portID);
    this.use$ = this.portService.useGet(this.portID);
    this.vlan$ = this.portService.vlanGet(this.portID);
    this.alias$ = this.portService.aliasGet(this.portID);
  }
}
