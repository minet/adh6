import { Component, OnInit } from '@angular/core';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import {AbstractDevice, AbstractMember, Device, DeviceService, Member, MemberService, Room} from '../api';
import {ActivatedRoute, Router} from '@angular/router';

@Component({
  selector: 'app-cotisant-recotisation',
  templateUrl: './cotisant-recotisation.component.html',
  styleUrls: ['./cotisant-recotisation.component.css']
})
export class CotisantRecotisationComponent implements OnInit {
  private device$: Observable<Array<Device>>;
  private mac$: Observable<string>;
  private member$: Observable<any>;
  private route: ActivatedRoute;
  private redirect$: Observable<any>;
  private macDevice: string;
  private adherent: Member;
  private room: Room;
  constructor(public deviceService: DeviceService,
              public memberService: MemberService,
              ) { }

  ngOnInit() {
    this.mac$ = this.route.params.pipe( map (params => params['client_mac']));
    this.redirect$ = this.route.params.pipe( map(params => params['client_mac']));

    this.macDevice = this.mac$.toString();
    let abstractDevice: AbstractDevice; /// création filtre de la requete API
    if (this.mac$) {
      abstractDevice = {
        mac: this.macDevice
      };
    }

    this.device$ = this.deviceService.deviceGet(1, 0, '', abstractDevice, 'body');
    this.device$.subscribe(
      devices => this.adherent = (devices[0])
    );

    let abstractMember: AbstractMember;
    abstractMember = {id: this.adherent.id};
    this.member$ = this.memberService.memberGet(1, 0, '', abstractMember, 'body');
    this.member$.subscribe(
      members => this.room = members.room);
  }

  public setDate(nb: number) {
    const today = new Date();
    today.setMonth(today.getMonth() + nb);
    return today;
  }
}
