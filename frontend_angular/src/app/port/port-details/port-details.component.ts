import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable, tap} from 'rxjs';
import {PortService, Port} from '../../api';
import {ActivatedRoute, Router} from '@angular/router';
import {NotificationsService} from 'angular2-notifications';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-port-details',
  templateUrl: './port-details.component.html',
  styleUrls: ['./port-details.component.css']
})
export class PortDetailsComponent implements OnInit, OnDestroy {
  vlanForm: FormGroup;
  port$: Observable<Port>;
  portID: number;
  switchID: number;

  changeVlanVisible = false;
  selectedVlan: number = 1;

  portAliasString: string;
  portSpeed: string ;

  private sub: any;

  public mab$: Observable<boolean>;
  public auth$: Observable<boolean>;
  public use$: Observable<string>;
  public status$: Observable<boolean>;
  public vlan$: Observable<number>;

  constructor(
    private portService: PortService,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private notif: NotificationsService,
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
  getAuth(state: boolean): string {
    return (state) ? 'ACTIVÉ' : 'DÉSACTIVÉ';
  }
  getMABStatus(state: boolean): string {
    return (state) ? 'ACTIVÉ' : 'DÉSACTIVÉ';
  }
  getAction(state: boolean): string {
    return (state) ? 'ACTIVER' : 'DÉSACTIVER';
  }

  public toggleStatus(): void {
    this.status$ = this.portService.portPortIdStatePut(this.portID);
  }

  public toggleMAB(): void {
    this.mab$ = this.portService.portPortIdMabPut(this.portID);
  }

  public toggleAuth(): void {
    this.auth$ = this.portService.portPortIdAuthPut(this.portID);
  }

  toogleVLANForm() {
    this.changeVlanVisible = !this.changeVlanVisible;
  }

  submitVLAN() {
    const v = this.vlanForm.value;
    this.portService.portPortIdVlanPut(v.vlanNumber, this.portID)
      .subscribe(() => {
        this.vlan$ = this.portService.vlanGet(this.portID);
        this.notif.success('VLAN assigned');
        this.toogleVLANForm();
      });
  }

  IfRoomExists(roomNumber) {
    console.log(roomNumber);
    if (roomNumber == null) {
      this.notif.error('This port is not assigned to a room');
    } else {
      this.router.navigate(['/room/view', roomNumber.roomNumber]);
    }
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.switchID = +params['switch_id'];
      this.portID = +params['port_id'];
      this.port$ = this.portService.portPortIdGet(this.portID);
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
    this.vlan$ = this.portService.vlanGet(this.portID)
      .pipe(
        tap(vlan => this.vlanForm.patchValue({vlanNumber: vlan}))
      );
    this.portService.aliasGet(this.portID)
      .subscribe((alias) => {
        this.portAliasString = alias;
      });
    this.portService.speedGet(this.portID)
      .subscribe((speed) => {
        this.portSpeed = speed;
      });
  }
}
