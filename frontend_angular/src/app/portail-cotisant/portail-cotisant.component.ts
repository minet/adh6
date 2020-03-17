import { Component, OnInit } from '@angular/core';
import {SCOPE_LIST} from '../config/scope.config';

@Component({
  selector: 'app-portail-cotisant',
  templateUrl: './portail-cotisant.component.html',
  styleUrls: ['./portail-cotisant.component.css']
})
export class PortailCotisantComponent implements OnInit {
  constructor() { }
  private expiration = 0;
  private mac = 0;
  private chambre = 0;
  private autre = 0;

  SCOPE_LIST = SCOPE_LIST;

  ngOnInit() {
  }

  afficheExpiration() {
    this.expiration = 1 - this.expiration;
  }

  afficheMac() {
    this.mac = 1 - this.mac;
  }

  afficheChambre() {
    this.chambre = 1 - this.chambre;
  }

  afficheAutre() {
    this.autre = 1 - this.autre;
  }
}


