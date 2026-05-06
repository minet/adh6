import {CommonModule} from "@angular/common";
import {Component, Input, OnInit} from "@angular/core";
import {map, Observable, of, shareReplay, switchMap} from "rxjs";
import {
  AbstractDevice,
  DeviceFilter,
  DeviceService,
  MemberService,
  Device,
} from "../api";
import {PaginationComponent} from "../pagination/pagination.component";
import {SearchPage} from "../search-page";
import {RouterModule, ActivatedRoute} from "@angular/router";
import {HttpResponse} from "@angular/common/http";

@Component({
  imports: [CommonModule, PaginationComponent, RouterModule],
  selector: "app-device-list",
  templateUrl: "./device-list.component.html",
})
export class DeviceListComponent extends SearchPage<Device> implements OnInit {
  public memberUsernames: Map<number, Observable<string>> = new Map<
    number,
    Observable<string>
  >();

  constructor(
    private readonly deviceService: DeviceService,
    private readonly memberService: MemberService,
    private readonly route: ActivatedRoute,
  ) {
    super((terms, page) =>
      (this.deviceService
        .deviceGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          <DeviceFilter>{terms: terms},
          ["id", "mac", "ipv4Address", "ipv6Address", "connectionType", "member", "name", "wifiPassword", "vendor", "mab"] as any,
          "response",
        ) as Observable<HttpResponse<Device[]>>)
        .pipe(
          map((response) => {
            if (response.body) {
              for (const device of response.body) {
                if (device.member && !this.memberUsernames.has(device.id!)) {
                  this.memberUsernames.set(device.id!, this.memberUsername$(device));
                }
              }
            }
            return response;
          }),
        ),
    );
  }

  override ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      this.getSearchResult();
    });
  }

  getUsername(id: number) {
    return this.memberUsernames.get(id);
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }

  public memberUsername$(device: Device): Observable<string> {
    if (!device.member) {
      return of("");
    }
    return this.memberService
      .memberIdGet(device.member, ["username"])
      .pipe(
        shareReplay(1),
        map((result) => {
          return result.username || "";
        }),
      );
  }
}
