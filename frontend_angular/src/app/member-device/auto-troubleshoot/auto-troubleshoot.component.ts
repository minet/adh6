import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { Member, MemberService, MemberStatus } from '../../api';

@Component({
  selector: 'app-auto-troubleshoot',
  template: `
  <ng-container *ngIf="statuses$ | async as statuses">
    <div class="alert alert-danger mt-4" *ngIf="statuses.length > 0">
      <h4 i18n="dashboard auto troubleshoot">Dépannage automatique</h4>
      <ul class="text-left">
        <li *ngFor="let status of statuses">
          <ng-container *ngIf="status.status === 'LOGIN_INCORRECT_WRONG_PASSWORD'" i18n="login incorrect wrong password">Mot de passe incorrect pour l'appareil <code>{{status.comment}}</code> ({{status.lastTimestamp | date: 'short'}})</ng-container>
          <ng-container *ngIf="status.status === 'LOGIN_INCORRECT_WRONG_MAC'" i18n="login incorrect wrong mac">Vous avez essayé de vous connecter avec l'appareil <code>{{status.comment}}</code>, mais cet appareil n'est pas ajouté à votre compte ({{status.lastTimestamp | date: 'short'}})</ng-container>
          <ng-container *ngIf="status.status === 'LOGIN_INCORRECT_WRONG_USER'" i18n="login incorrect wrong user">Vous avez essayé de vous connecter avec votre appareil <code>{{status.comment}}</code> mais depuis un autre compte ({{status.lastTimestamp | date: 'short'}})</ng-container>
          <ng-container *ngIf="status.status === 'LOGIN_INCORRECT_SSL_ERROR'" i18n="login incorrect ssl error">L'appareil <code>{{status.comment}}</code> est mal configuré, vérifiez la configuration via les tutoriels, en particulier la présence de MSCHAPv2 et la non-validation du certificat ({{status.lastTimestamp | date: 'short'}})</ng-container>
        </li>
      </ul>
    </div>
  </ng-container>
  `
})
export class AutoTroubleshootComponent implements OnInit {
  statuses$: Observable<MemberStatus[]>;

  @Input() member: Member;

  constructor(private memberService: MemberService) { }

  ngOnInit(): void {
    this.statuses$ = this.memberService.memberIdStatusesGet(this.member.id, 'body');
  }

}
