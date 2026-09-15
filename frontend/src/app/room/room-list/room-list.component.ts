import {Component, DestroyRef, inject, OnInit} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {RouterModule} from "@angular/router";
import {FormControl, ReactiveFormsModule} from "@angular/forms";
import {AsyncPipe} from "@angular/common";
import {PaginationComponent} from "../../pagination/pagination.component";
import {AbstractRoom, RoomService} from "../../api";
import {SearchPage} from "../../search-page";
import {ComboboxComponent, ComboboxOption} from "../../ui/combobox.component";
import {loadRooms} from "../../ui/entity-options";

@Component({
  imports: [
    RouterModule,
    ReactiveFormsModule,
    AsyncPipe,
    PaginationComponent,
    ComboboxComponent,
  ],
  selector: "app-rooms",
  templateUrl: "./room-list.component.html",
  standalone: true,
})
export class RoomListComponent
  extends SearchPage<AbstractRoom>
  implements OnInit
{
  readonly roomSearch = new FormControl("", {nonNullable: true});
  roomOptions: ComboboxOption[] = [];
  optionsLoading = true;
  optionsUnavailable = false;
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
    loadRooms(this.roomService)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (rooms) => {
          this.roomOptions = rooms.map((room) => ({
            value: String(room.roomNumber),
            label: [room.roomNumber, room.description]
              .filter((value) => value != null && value !== "")
              .join(" : "),
          }));
          this.optionsLoading = false;
        },
        error: () => {
          this.optionsLoading = false;
          this.optionsUnavailable = true;
        },
      });
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
