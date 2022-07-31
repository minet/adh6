import { Component, OnInit } from '@angular/core';
import { map, Observable, shareReplay } from 'rxjs';
import { AbstractDevice, DeviceService, MemberService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-device-list',
  templateUrl: './device-list.component.html',
  styleUrls: ['./device-list.component.css']
})
export class DeviceListComponent extends SearchPage<AbstractDevice> implements OnInit {
  memberUsernames: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();
  constructor(
    private deviceService: DeviceService,
    private memberService: MemberService
  ) {
    super((terms, page) => this.deviceService.deviceGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, undefined, "response")
      .pipe(
        map(response => {
          for (let i of response.body) {
            if (i.member && !this.memberUsernames.has(i.member)) {
              this.memberUsernames.set(i.member, this.memberUsername$(i.member));
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
    return this.memberService.memberIdGet(id, ["username"])
      .pipe(
        shareReplay(1),
        map(result => {
          return result.username
        })
      );
  }
}
