import {Component, DestroyRef, inject, OnInit} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {RouterModule} from "@angular/router";
import {FormControl, ReactiveFormsModule} from "@angular/forms";
import {AsyncPipe, DatePipe} from "@angular/common";
import {AblePipe} from "@casl/angular";
import {PaginationComponent} from "../pagination/pagination.component";
import {MiniRouter, MiniRouterService} from "../api";
import {SearchPage} from "../search-page";
import {
  CONFIG_STATE_LABELS,
  depositBadge,
  MODEL_LABELS,
  OVERDUE_LABEL,
} from "./labels";

type LoanedFilter = "all" | "loaned" | "available" | "overdue";

// The whole fleet fits on one page, like the former spreadsheet
const PAGE_SIZE = 100;

@Component({
  imports: [
    RouterModule,
    ReactiveFormsModule,
    AsyncPipe,
    DatePipe,
    AblePipe,
    PaginationComponent,
  ],
  selector: "app-mini-router-list",
  templateUrl: "./mini-router-list.component.html",
})
export class MiniRouterListComponent
  extends SearchPage<MiniRouter>
  implements OnInit
{
  readonly search$ = new FormControl("", {nonNullable: true});
  readonly loanedFilter = new FormControl<LoanedFilter>("all", {
    nonNullable: true,
  });
  readonly modelLabels = MODEL_LABELS;
  readonly configStateLabels = CONFIG_STATE_LABELS;
  readonly depositBadge = depositBadge;
  readonly overdueLabel = OVERDUE_LABEL;
  private readonly destroyRef = inject(DestroyRef);

  constructor(private readonly miniRouterService: MiniRouterService) {
    super((terms, page) => {
      const filter = this.loanedFilter.value;
      return this.miniRouterService.miniRouterGet(
        this.itemsPerPage,
        (page - 1) * this.itemsPerPage,
        terms,
        filter === "loaned" ? true : filter === "available" ? false : undefined,
        filter === "overdue" ? true : undefined,
        "response",
      );
    });
    this.itemsPerPage = PAGE_SIZE;
  }

  override ngOnInit() {
    super.ngOnInit();
    this.search$.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((term) => this.search(term));
    this.loanedFilter.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.resetSearch());
  }
}
