import { CommonModule } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Member } from '../api';
import { MailinglistComponent } from '../mailinglist/mailinglist.component';

@Component({
  standalone: true,
  imports: [CommonModule, MailinglistComponent, RouterModule],
  selector: 'app-account',
  template: `    
    <div class="box has-text-centered">
      <h4 *ngIf="isDepartureDateFuture, else invalidDate"
        i18n="dashboard active subscription|Describes until when a subscription is active">
        Votre abonnement est actif jusqu'au <strong>{{ member.departureDate | date }}</strong>
      </h4>
      <ng-template #invalidDate>
        <h4 class="text-danger" i18n="dashboard expired subscription|Describes when a subscription has expired">
          Votre abonnement a expiré le <strong>{{ member.departureDate | date }}</strong></h4>
      </ng-template>
      <hr>
      <div class="buttons has-addons is-centered">
        <a href="//payment.minet.net" role="button" class="button is-success" i18n="renew">
          Renouveler mon abonnement
        </a>
        <a [routerLink]="['/password/', member.id, 0 ]" role="button" class="button is-danger" i18n="password change">
          Changer le mot de passe
        </a>
      </div>
    </div>
    <div class="box">
      <app-mailinglist [mailinglistValue]="member.mailinglist" [memberId]="member.id"></app-mailinglist>
    </div>
    <div class="box has-text-centered">
      <hr>
      <p>
        <span i18n="@@email">mail</span> : <code>{{ member.email }}</code>
      </p>
      <ng-container *ngIf="member.ip !== null && member.subnet !== null">
        <hr>
        <p>
          <span i18n="wifi public ipv4|Shows a user their public IPv4">Votre adresse IPv4 publique est :</span>
          <code>{{ member.ip }}</code>
        </p>
        <p>
          <span i18n="wifi private subnetv4|Shows a user their private IPv4 subnet">Votre sous-réseau IPv4 privé est :</span>
          <code>{{ member.subnet }}</code>
        </p>
      </ng-container>
    </div>
  `
})
export class AccountComponent implements OnInit {
  @Input() member: Member;
  public isDepartureDateFuture = false;

  constructor() { }

  ngOnInit(): void {
    this.isDepartureDateFuture = new Date() < new Date(this.member.departureDate);
  }
}
