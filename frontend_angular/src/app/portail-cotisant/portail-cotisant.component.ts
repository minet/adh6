import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-portail-cotisant',
  templateUrl: './portail-cotisant.component.html',
  styleUrls: ['./portail-cotisant.component.css']
})
export class PortailCotisantComponent implements OnInit {
  private expiration = 0;
  private mac = 0;
  private chambre = 0;
  private autre = 0;
  constructor() { }

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


