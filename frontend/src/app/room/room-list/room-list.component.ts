import {Component, OnInit} from "@angular/core";
import {RouterModule} from "@angular/router";
import {ReactiveFormsModule} from "@angular/forms";
import {AsyncPipe} from "@angular/common";
import {PaginationComponent} from "../../pagination/pagination.component";
import {AbstractRoom, RoomService} from "../../api";
import {SearchPage} from "../../search-page";

@Component({
  imports: [RouterModule, ReactiveFormsModule, AsyncPipe, PaginationComponent],
  selector: "app-rooms",
  templateUrl: "./room-list.component.html",
  standalone: true,
})
export class RoomListComponent
  extends SearchPage<AbstractRoom>
  implements OnInit
{
  constructor(public roomService: RoomService) {
    super((terms, page) =>
      this.roomService.roomGet(
        this.itemsPerPage,
        (page - 1) * this.itemsPerPage,
        terms,
        undefined,
        undefined,
        "response",
      ),
    );
  }

  override ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
