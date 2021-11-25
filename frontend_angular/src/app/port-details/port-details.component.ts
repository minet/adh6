import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {PortService} from '../api';
import {Port} from '../api';
import {ActivatedRoute, Router} from '@angular/router';
import {NotificationsService} from 'angular2-notifications';

@Component({
  selector: 'app-port-details',
  templateUrl: './port-details.component.html',
  styleUrls: ['./port-details.component.css']
})
export class PortDetailsComponent implements OnInit, OnDestroy {

  port$: Observable<Port>;
  portID: number;
  switchID: number;

  vlans = [
    {'name': '1', 'value': '1'},
    {'name': 'dev: 103', 'value': '103'},
    {'name': 'prod: 102', 'value': '102'},
    {'name': '999', 'value': '999'}
  ];

  vlan: number;
  changeVlanVisible = false;
  selectedVlan = '1';

  portAliasString: string;
  portSpeed: string ;

  private sub: any;

  public mab$: Observable<boolean>;
  public auth$: Observable<boolean>;
  public use$: Observable<string>;
  public status$: Observable<boolean>;
  public vlan$: Observable<number>;

  constructor(
    public portService: PortService,
    private route: ActivatedRoute,
    private router: Router,
    private notif: NotificationsService,
  ) {
  }

  getUse(state: string): string {
    return (state == "authorized") ? 'Le port est actuellement utilisé' : 'Le port n\'est pas actuellement utilisé';
  }
  getStatus(state: boolean): string {
    return (state) ? 'OUVERT' : 'FERMÉ';
  }
  getAuth(state: boolean): string {
    return (state) ? 'ACTIVÉ' : 'DESACTIVÉ';
  }
  getMABStatus(state: boolean): string {
    return (state) ? 'ACTIVÉ' : 'DEACTIVÉ';
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

  changeVlan(newVlan) {
    this.portService.portPortIdVlanPut(newVlan, this.portID)
      .subscribe(() => {
        this.vlan$ = this.portService.vlanGet(this.portID);
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
    this.vlan$ = this.portService.vlanGet(this.portID);
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
