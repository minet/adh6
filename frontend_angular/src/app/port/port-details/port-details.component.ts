import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {PortService, Port} from '../../api';
import {ActivatedRoute, Router} from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import Swal from 'sweetalert2';
import { AppConstantsService } from '../../app-constants.service';
import { NotificationService } from '../../notification.service';

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

  portSpeed: string ;

  private sub: any;

  public mab: boolean;
  public auth: boolean;
  public use: string;
  public status: boolean;
  public alias: string;
  public vlan: number;

  constructor(
    private portService: PortService,
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
    this.portService.portPortIdStatePut(this.portID)
      .subscribe(value => {
        this.status = value;
        this.notificationService.successNotification("État du port modifié");
      });
  }

  public toggleMAB(): void {
    this.portService.portPortIdMabPut(this.portID)
      .subscribe(value => {
        this.mab = value;
        this.notificationService.successNotification("MAB modifié");
      });
  }

  public toggleAuth(): void {
    this.portService.portPortIdAuthPut(this.portID)
      .subscribe(value => {
        this.notificationService.successNotification("Authentification modifiée");
        if (!value) {
          Swal.fire({
            title: 'Entrer le VLAN',
            icon: 'question',
            input: 'number',
            inputLabel: 'VLAN 1',
            inputPlaceholder: 'Entrer le VLAN',
          }).then((result) => {
            if (result.isConfirmed) {
              this.auth = value;
              console.log(result);
              this.submitVLAN(result.value);
              return;
            }
            if (result.isDenied) {
              this.toggleAuth();
            }
          });
        } else {
          this.auth = value;
          this.submitVLAN(1);
        }
      });
  }

  submitVLAN(vlan: number) {
    this.portService.portPortIdVlanPut(vlan, this.portID)
      .subscribe(() => {
        this.notificationService.successNotification("VLAN modifié: " + vlan);
        this.vlan = vlan;
      });
  }

  IfRoomExists(roomNumber) {
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
      this.port$ = this.portService.portPortIdGet(this.portID);
    });

    this.refreshInfo();
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  refreshInfo(): void {
    this.portService.authGet(this.portID)
      .subscribe(value => {
        this.auth = value;
      });
    this.portService.stateGet(this.portID)
      .subscribe(value => {
        this.status = value;
      });
    this.portService.mabGet(this.portID)
      .subscribe(value => {
        this.mab = value;
      });
    this.portService.useGet(this.portID)
      .subscribe(value => {
        this.use = value;
      });
    this.portService.vlanGet(this.portID)
      .subscribe(value => {
        this.vlan = value;
      });
    this.portService.aliasGet(this.portID)
      .subscribe(alias => {
        this.alias = alias;
      });
  }
}
