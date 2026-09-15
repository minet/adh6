import {Component, DestroyRef, inject, OnInit} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {RouterModule} from "@angular/router";
import {FormControl, ReactiveFormsModule} from "@angular/forms";
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
  readonly roomSearch = new FormControl("", {nonNullable: true});
  private readonly destroyRef = inject(DestroyRef);
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
    this.roomSearch.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((term) => this.search(term));
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
