import {CommonModule} from "@angular/common";
import {Component, Input, OnInit} from "@angular/core";
import {RouterModule} from "@angular/router";
import {map, Observable, shareReplay} from "rxjs";
import {AbstractPort, PortService, RoomService, SwitchService} from "../../api";
import {PaginationComponent} from "../../pagination/pagination.component";
import {SearchPage} from "../../search-page";

@Component({
  imports: [CommonModule, RouterModule, PaginationComponent],
  selector: "app-port-list",
  templateUrl: "./list.component.html",
})
export class PortListComponent
  extends SearchPage<AbstractPort>
  implements OnInit
{
  @Input() switchId: number | undefined;
  cachedSwitchDescription: Map<number, Observable<string>> = new Map<
    number,
    Observable<string>
  >();
  cachedRoomDescription: Map<number, Observable<string>> = new Map<
    number,
    Observable<string>
  >();

  private filter: AbstractPort = {};
  constructor(
    private readonly portService: PortService,
    private readonly roomService: RoomService,
    private readonly switchService: SwitchService,
  ) {
    super((terms, page) =>
      this.portService
        .portGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          terms,
          this.filter,
          ["portNumber", "room", "switchObj"],
          "response",
        )
        .pipe(
          map((response) => {
            if (!response.body) return response;
            for (const p of response.body) {
              if (p.room && !this.cachedRoomDescription.has(p.room)) {
                this.cachedRoomDescription.set(
                  p.room,
                  this.roomService.roomIdGet(p.room).pipe(
                    shareReplay(1),
                    map((room) => room?.description || ""),
                  ),
                );
              }
              if (
                p.switchObj &&
                !this.cachedSwitchDescription.has(p.switchObj)
              ) {
                this.cachedSwitchDescription.set(
                  p.switchObj,
                  this.switchService.switchIdGet(p.switchObj).pipe(
                    shareReplay(1),
                    map((s) => s?.description || ""),
                  ),
                );
              }
            }
            return response;
          }),
        ),
    );
  }

  override ngOnInit() {
    super.ngOnInit();
    this.filter = this.switchId ? <AbstractPort>{switchObj: this.switchId} : {};
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
