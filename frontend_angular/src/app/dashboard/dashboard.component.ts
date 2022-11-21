import { Component, OnInit } from '@angular/core';
import { Member, MiscService } from '../api';
import { map, Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { AccountComponent } from './tab-account.component';
import { MemberDeviceModule } from '../member-device/member-device.module';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { animate, animateChild, group, query, style, transition, trigger } from '@angular/animations';


export const slider = trigger('routeAnimations', [
  transition(':increment', slideTo('right') ),
  transition(':decrement', slideTo('left') ),
]);

function slideTo(direction: string) {
    return [
        query(':enter, :leave', [
            style({
                position: 'absolute',
                top: 0,
                [direction]: 0,
                width: '100%'
            })
        ]),
        query(':enter', [
            style({ [direction]: '-100%'})
        ]),
        group([
            query(':leave', [animate('600ms ease', style({ [direction]: '100%', opacity: 0}))]),
            query(':enter', [animate('600ms ease', style({ [direction]: '0%', opacity: 1}))])
        ]),
        query(':leave', animateChild()),
        query(':enter', animateChild()),
    ];
}

@Component({
  standalone: true,
  imports: [CommonModule, RouterModule, AccountComponent, MemberDeviceModule],
  animations: [slider],
  selector: 'app-dashboard',
  styles: ['img { height: 130px; }'],
  template: `
  <div class="columns column is-centered">
    <figure>
      <img alt="adh6 logo" src="../assets/adh6.min.svg">
    </figure>
  </div>
  <ng-container *ngIf="member$ | async as member">
    <div class="tabs is-centered is-large">
      <ul>
        <li routerLinkActive="is-active">
          <a i18n="own devices" [routerLink]="['device']">Mes appareils</a>
        </li>
        <li routerLinkActive="is-active">
          <a i18n="own account" [routerLink]="['profile']">Mon compte</a>
        </li>
      </ul>
    </div>
    <div class="container">
      <div [@routeAnimations]="prepareRoute(outlet)" >
        <router-outlet #outlet="outlet" (activate)="onOutletLoaded($event, member)"></router-outlet>
      </div>
    </div>
  </ng-container>
  `
})
export class DashboardComponent implements OnInit {
  public member$: Observable<Member>;
  public currentTab = "device";

  constructor(
    private miscService: MiscService,
    private router: Router
  ) {
    this.member$ = this.miscService.profile().pipe(map(r => r.member))
  }

  ngOnInit(): void {
    this.router.navigate(['dashboard', 'device'])
  }

  public onOutletLoaded(component, member: Member) {
    component.member = member;
  }
  
  prepareRoute(outlet: RouterOutlet) {
    return outlet && outlet.activatedRouteData && outlet.activatedRouteData['animation'];
  }
}
