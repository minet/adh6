import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { map, Observable, shareReplay, switchMap } from 'rxjs';
import { AbstractDevice, DeviceFilter, DeviceService, MemberService } from '../api';
import { PaginationComponent } from '../pagination/pagination.component';
import { SearchPage } from '../search-page';

@Component({
  standalone: true,
  imports: [CommonModule, PaginationComponent],
  selector: 'app-device-list',
  template: `
  <input #searchBox id="search-box" placeholder="Rechercher..." (keyup)="search(searchBox.value)" class="input is-fullwidth" type="text" />
  <br>
  <table class="table is-hoverable is-fullwidth is-clickable">
    <thead>
      <tr>
        <th style="width: 33%;">Utilisateur</th>
        <th style="width: 33%;">MAC de l'appareil</th>
        <th style="width: 33%;">Type d'appareil</th>
      </tr>
    </thead>
    <tbody *ngIf="result$ | async as result; else loadingTable">
      <ng-container *ngFor="let i of result">
        <ng-container *ngIf="getDevice(i) | async as device">
          <tr [routerLink]="['/member/view' , device.member]">
            <td>{{ (getUsername(i) | async) || "chargement..." }}</td>
            <td>{{ device.mac }}</td>
            <td>{{ device.connectionType }}</td>
          </tr>
        </ng-container>
      </ng-container>
    </tbody>
  </table>
  <app-pagination [maxItems]="maxItems" (pageChange)="handlePageChange($event)"></app-pagination>
  <ng-template #loadingTable>
    <tr>
      <td colspan="42">
        <div class="notification is-info is-light has-text-centered">
          <h4 class="title is-4">Chargement ...</h4>
        </div>
      </td>
    </tr>
  </ng-template>
  `
})
export class DeviceListComponent extends SearchPage<number> implements OnInit {
  public memberUsernames: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();
  public cachedDevices: Map<Number, Observable<AbstractDevice>> = new Map();
  constructor(
    private deviceService: DeviceService,
    private memberService: MemberService
  ) {
    super((terms, page) => this.deviceService.deviceGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, <DeviceFilter>{ terms: terms }, "response")
      .pipe(
        map(response => {
          for (let i of response.body) {
            this.cachedDevices.set(+i, this.deviceService.deviceIdGet(i).pipe(shareReplay(1)));
            if (i && !this.memberUsernames.has(i)) {
              this.memberUsernames.set(i, this.memberUsername$(i));
            }
          }
          return response;
        })
      )
    )
  }

  ngOnInit() {
    super.ngOnInit();
  }

  getUsername(id: number) {
    return this.memberUsernames.get(id);
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }

  public memberUsername$(id: number): Observable<string> {
    return this.cachedDevices.get(id).pipe(
      switchMap(
        response => {
          return this.memberService.memberIdGet(response.member, ["username"])
            .pipe(
              shareReplay(1),
              map(result => {
                return result.username
              })
            )
        })
    );
  }

  public getDevice(id: number) {
    return this.cachedDevices.get(id)
  }
}
