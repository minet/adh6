import {CommonModule} from "@angular/common";
import {Component, Input, OnInit} from "@angular/core";
import {map, Observable, shareReplay, switchMap} from "rxjs";
import {
  AbstractDevice,
  DeviceFilter,
  DeviceService,
  MemberService,
} from "../api";
import {PaginationComponent} from "../pagination/pagination.component";
import {SearchPage} from "../search-page";
import {RouterModule, ActivatedRoute} from "@angular/router";
import {AbstractAccount} from "../api/model/abstractAccount";

@Component({
  imports: [CommonModule, PaginationComponent, RouterModule],
  selector: "app-device-list",
  templateUrl: "./device-list.component.html",
})
export class DeviceListComponent extends SearchPage<number> implements OnInit {
  public memberUsernames: Map<number, Observable<string>> = new Map<
    number,
    Observable<string>
  >();
  public cachedDevices: Map<number, Observable<AbstractDevice>> = new Map();
  @Input() abstractAccountFilter: AbstractAccount = {};
  constructor(
    private readonly deviceService: DeviceService,
    private readonly memberService: MemberService,
    private readonly route: ActivatedRoute,
  ) {
    super((terms, page) =>
      this.deviceService
        .deviceGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          <DeviceFilter>{terms: terms},
          "response",
        )
        .pipe(
          map((response) => {
            for (const i of response.body) {
              this.cachedDevices.set(
                +i,
                this.deviceService.deviceIdGet(i).pipe(shareReplay(1)),
              );
              if (i && !this.memberUsernames.has(i)) {
                this.memberUsernames.set(i, this.memberUsername$(i));
              }
            }
            return response;
          }),
        ),
    );
  }

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      if (params["member"] !== undefined) {
        this.abstractAccountFilter.member = +params["member"];
      }
      this.getSearchResult();
    });
  }

  getUsername(id: number) {
    return this.memberUsernames.get(id);
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }

  public memberUsername$(id: number): Observable<string> {
    return this.cachedDevices.get(id).pipe(
      switchMap((response) => {
        return this.memberService
          .memberIdGet(response.member, ["username"])
          .pipe(
            shareReplay(1),
            map((result) => {
              return result.username;
            }),
          );
      }),
    );
  }

  public getDevice(id: number) {
    return this.cachedDevices.get(id);
  }
}
