import { Component, OnInit } from '@angular/core';
import { map, Observable, shareReplay, switchMap } from 'rxjs';
import { AbstractDevice, DeviceFilter, DeviceService, MemberService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-device-list',
  templateUrl: './device-list.component.html',
  styleUrls: ['./device-list.component.css']
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
