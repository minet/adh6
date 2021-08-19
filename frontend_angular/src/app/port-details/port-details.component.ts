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

  portStatusString = 'N/A';
  portStatus: boolean;

  portAuthString = 'N/A';
  portAuth: boolean;

  portMabString = 'N/A';
  portMab: boolean;

  portAliasString: boolean;

  private sub: any;

  constructor(
    public portService: PortService,
    private route: ActivatedRoute,
    private router: Router,
    private notif: NotificationsService,
  ) {
  }

  setStatus(state) {
    if (state) {
      this.portStatusString = 'OUVERT';
    } else {
      this.portStatusString = 'FERMÉ';
    }
    this.portStatus = state;
  }

  toggleStatus() {
    this.portService.portPortIdStatePut(!this.portStatus, this.portID)
      .subscribe(() => {
        this.setStatus(!this.portStatus);
      });
  }

  setAuth(state) {
    if (state) {
      this.portAuthString = 'ACTIVÉ';
    } else {
      this.portAuthString = 'DÉSACTIVÉ';
    }
    this.portAuth = state;
  }

  setMabStatus(state) {
    if (state) {
      this.portMabString = 'ACTIVÉ';
    } else {
      this.portMabString = 'DÉSACTIVÉ';
    }
    this.portMab = state;
  }

  toggleMabStatus() {
    this.portService.portPortIdMabPut(!this.portMab, this.portID)
      .subscribe(() => {
        this.setMabStatus(!this.portMab);
      });
  }

  changeVlan(newVlan) {
    this.portService.portPortIdVlanPut(newVlan, this.portID)
      .subscribe((vlan) => {
        this.vlan = vlan;
      });
  }

  IfRoomExists(roomNumber) {
    if (roomNumber == null) {
      this.notif.error('This port is not assigned to a room');
    } else {
      this.router.navigate(['/room/view', roomNumber]);
    }
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.switchID = +params['switch_id'];
      this.portID = +params['port_id'];
      this.port$ = this.portService.portPortIdGet(this.portID);
    });

/*    this.portService.authGet(this.portID)
      .subscribe((status) => {
        this.setAuth(status);
      });
*/
    this.portService.stateGet(this.portID)
      .subscribe((status) => {
        this.setStatus(status);
      });
    this.portService.vlanGet(this.portID)
      .subscribe((vlan) => {
        this.vlan = vlan;
      });
    this.portService.mabGet(this.portID)
      .subscribe((mabState) => {
        this.setMabStatus(mabState);
      });
    this.portService.aliasGet(this.portID)
      .subscribe((alias) => {
        this.portAliasString = alias;
      });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

}
