import { Component, OnInit } from '@angular/core';
import {map} from 'rxjs/operators';
import {ActivatedRoute, Router} from '@angular/router';
import {Observable} from 'rxjs';
import {AbstractDevice, AbstractMember, Device, DeviceService, Member, MemberService} from '../api';


// @ts-ignore
@Component({
  selector: 'app-portail-cotisant',
  templateUrl: './portail-cotisant.component.html',
  styleUrls: ['./portail-cotisant.component.css']
})
export class PortailCotisantComponent implements OnInit {

  private expiration: string;
  private macDevice: string;
  private adherent: Member;
  private existRoom: boolean;
  private route: ActivatedRoute;
  private device$: Observable<Array<Device>>;
  private mac$: Observable<string>;
  private redirect$: Observable<any>;
  private member$: Observable<any>;



  constructor(
    public deviceService: DeviceService,
    public memberService: MemberService,
  ) {}

// tslint:disable-next-line:max-line-length
// idée : récupérer l'adresse mac -> faire requete API pour filtrer les devices -> récupérer le "member" -> on obtient les autres infos nécessaires

  ngOnInit() {

    this.mac$ = this.route.params.pipe( // on récupère l'adresse mac, le redirect depuis l'URL
      map(params => params['client_mac'])
    );

    this.macDevice = this.mac$.toString();
    this.redirect$ = this.route.params.pipe( // on récupère le redirect
      map(params => params['client_mac'])
    );


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
    abstractMember = { id: this.adherent.id};
    this.member$ = this.memberService.memberGet(1, 0, '', abstractMember, 'body'); // on récupére l'adhérent qui contient la chambre

    this.member$.subscribe(
      members => this.existRoom = (members.room !== undefined) // on regarde s'il y a une chambre
    );
    return this.existRoom; // on retourne le fait qu'il y ait une chambre
    }



 /* afficheExpiration() {
    this.expiration = 1 - this.expiration;
  }

  afficheMac() {
    this.mac = 1 - this.mac;
  }

  afficheChambre() {
    this.chambre = 1 - this.chambre;
  }
 */
}


