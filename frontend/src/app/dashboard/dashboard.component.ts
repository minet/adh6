import {CommonModule} from "@angular/common";
import {Component, inject} from "@angular/core";
import {RouterModule} from "@angular/router";
import {map, Observable, filter} from "rxjs";
import {Member, MiscService} from "../api";
import {MemberDeviceModule} from "../member-device/member-device.module";
import {ThemeService} from "../theme.service";

@Component({
  imports: [CommonModule, RouterModule, MemberDeviceModule],
  selector: "app-dashboard",
  styles: ["img { height: 130px; }"],
  template: `
    <div class="columns column is-centered">
      <figure>
        <img
          alt="adh6 logo"
          [src]="
            theme.isDark() ? 'assets/adh6-dark.min.svg' : 'assets/adh6.min.svg'
          " />
      </figure>
    </div>
    <ng-container *ngIf="member$ | async as member">
      <div class="tabs is-centered is-large">
        <ul>
          <li routerLinkActive="is-active">
            <a i18n="@@dashboard.tab.devices" [routerLink]="['device']">Mes appareils</a>
          </li>
          <li routerLinkActive="is-active">
            <a i18n="@@dashboard.tab.account" [routerLink]="['profile']">Mon compte</a>
          </li>
        </ul>
      </div>
      <div class="container">
        <router-outlet
          (activate)="onOutletLoaded($event, member)"></router-outlet>
      </div>
    </ng-container>
  `,
})
export class DashboardComponent {
  protected readonly theme = inject(ThemeService);
  public member$: Observable<Member>;
  public currentTab = "device";

  constructor(private readonly miscService: MiscService) {
    this.member$ = this.miscService.profile().pipe(
      map((r) => r.member),
      filter((member): member is Member => member != null),
    );
  }

  public onOutletLoaded(component: {member?: Member}, member: Member) {
    component.member = member;
  }
}
