import {CommonModule} from "@angular/common";
import {
  Component,
  DestroyRef,
  inject,
  Input,
  OnInit,
  OnChanges,
} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {HttpHeaders, HttpResponse} from "@angular/common/http";
import {FormControl, FormGroup, ReactiveFormsModule} from "@angular/forms";
import {RouterModule} from "@angular/router";
import {debounceTime, map, merge, Observable, of, shareReplay} from "rxjs";
import {AbstractPort, PortService, RoomService, SwitchService} from "../../api";
import {PaginationComponent} from "../../pagination/pagination.component";
import {SearchPage} from "../../search-page";
import {ComboboxComponent, ComboboxOption} from "../../ui/combobox.component";
import {RoomSelectComponent} from "../../ui/room-select.component";
import {loadSwitchOptions} from "../../ui/entity-options";

@Component({
  imports: [
    CommonModule,
    RouterModule,
    PaginationComponent,
    ReactiveFormsModule,
    ComboboxComponent,
    RoomSelectComponent,
  ],
  selector: "app-port-list",
  templateUrl: "./list.component.html",
})
export class PortListComponent
  extends SearchPage<AbstractPort>
  implements OnInit, OnChanges
{
  @Input() switchId: number | undefined;
  readonly filters = new FormGroup({
    room: new FormControl<number | null>(null),
    switchObj: new FormControl<number | null>(null),
  });
  switchOptions: ComboboxOption[] = [];
  switchesLoading = true;
  switchesUnavailable = false;
  private readonly destroyRef = inject(DestroyRef);
  private initialized = false;
  cachedSwitchDescription: Map<number, Observable<string>> = new Map<
    number,
    Observable<string>
  >();

  private filter: AbstractPort = {};
  constructor(
    private readonly portService: PortService,
    private readonly roomService: RoomService,
    private readonly switchService: SwitchService,
  ) {
    super((terms, page) => {
      if (this.filters.invalid) {
        return of(
          new HttpResponse<AbstractPort[]>({
            body: [],
            headers: new HttpHeaders({"x-total-count": "0"}),
          }),
        );
      }
      const {room, switchObj} = this.filters.getRawValue();
      this.filter = {
        ...(room != null ? {room} : {}),
        ...((this.switchId ?? switchObj) != null
          ? {switchObj: this.switchId ?? switchObj!}
          : {}),
      };
      return this.portService
        .portGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          terms,
          this.filter,
          ["portNumber", "room", "switchObj", "roomObj"],
          "response",
        )
        .pipe(
          map((response) => {
            if (!response.body) return response;
            for (const p of response.body) {
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
        );
    });
  }

  override ngOnInit() {
    this.initialized = true;
    this.filters.controls.switchObj.setValue(this.switchId ?? null, {
      emitEvent: false,
    });
    super.ngOnInit();
    merge(this.filters.valueChanges, this.filters.statusChanges)
      .pipe(debounceTime(0), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.refreshFilters());
    loadSwitchOptions(this.switchService)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (options) => {
          this.switchOptions = options;
          this.switchesLoading = false;
        },
        error: () => {
          this.switchesLoading = false;
          this.switchesUnavailable = true;
        },
      });
  }

  ngOnChanges(): void {
    if (this.initialized) {
      this.filters.controls.switchObj.setValue(this.switchId ?? null, {
        emitEvent: false,
      });
      this.refreshFilters();
    }
  }

  private refreshFilters(): void {
    this.resetSearch();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
