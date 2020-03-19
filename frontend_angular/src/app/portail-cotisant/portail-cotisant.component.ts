import { Component, OnInit } from '@angular/core';
import {SCOPE_LIST} from '../config/scope.config';
import {map} from 'rxjs/operators';
import {ActivatedRoute, Router} from '@angular/router';
import {Observable} from 'rxjs';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';

// @ts-ignore
@Component({
  selector: 'app-portail-cotisant',
  templateUrl: './portail-cotisant.component.html',
  styleUrls: ['./portail-cotisant.component.css']
})
export class PortailCotisantComponent implements OnInit {
  constructor() { }
  private expiration: string;
  private mac: Observable<any>;
  private chambre: FormGroup;
  private autre = 0;
  private redirect: Observable<any>;
  private route: ActivatedRoute;
  private fb: FormBuilder;


// tslint:disable-next-line:max-line-length
// idée : récupérer l'adresse mac -> faire requete API pour filtrer les devices -> récupérer le "member" -> on obtient les autres infos nécessaires
  SCOPE_LIST = SCOPE_LIST;

  // @ts-ignore
  ngOnInit() {
    this.mac = this.route.params.pipe( //on récupère l'adresse mac, le redirect depuis l'URL
      map(params => params['client_mac'])
    );
    this.redirect = this.route.params.pipe(
      map(params => params['client_mac'])
    );
    this.chambre = this.fb.group({
      'room': [[Validators.required, Validators.minLength(4), Validators.maxLength(4)]], }); //On récupère la chambre de l'adhérent avec une requete API (pas certain)
  }


 /* afficheExpiration() {
    this.expiration = 1 - this.expiration;
  }

  afficheMac() {
    this.mac = 1 - this.mac;
  }

  afficheChambre() {
    this.chambre = 1 - this.chambre;
  }   */

  afficheAutre() {
    this.autre = 1 - this.autre;
  }
}


