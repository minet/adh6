import {Component, Input, OnInit} from "@angular/core";
import {AccountService, AccountType} from "../../api";
import {SearchPage} from "../../search-page";
import {AbstractAccount} from "../../api/model/abstractAccount";
import {AppConstantsService} from "../../app-constants.service";

import {ActivatedRoute, RouterModule} from "@angular/router";
import {map, Observable, shareReplay} from "rxjs";
import {CommonModule} from "@angular/common";
import {PaginationComponent} from "../../pagination/pagination.component";

@Component({
  imports: [CommonModule, PaginationComponent, RouterModule],
  selector: "app-account-list",
  templateUrl: "./account-list.component.html",
})
export class AccountListComponent
  extends SearchPage<AbstractAccount>
  implements OnInit
{
  accountTypes: AccountType[] = [];
  @Input() abstractAccountFilter: AbstractAccount = {};
  cachedAccountType: Map<number, Observable<string>> = new Map<
    number,
    Observable<string>
  >();

  constructor(
    private readonly accountService: AccountService,
    private readonly route: ActivatedRoute,
    private readonly appConstantsService: AppConstantsService,
  ) {
    super((terms, page) =>
      this.accountService
        .accountGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          terms,
          this.abstractAccountFilter,
          ["name", "balance", "actif", "accountType"],
          "response",
        )
        .pipe(
          map((response) => {
            if (response.body) {
              for (const i of response.body) {
                if (
                  i.accountType &&
                  !this.cachedAccountType.has(i.accountType)
                ) {
                  this.cachedAccountType.set(
                    i.accountType,
                    this.accountService.accountTypeIdGet(i.accountType).pipe(
                      shareReplay(1),
                      map((result) => result.name || ""),
                    ),
                  );
                }
              }
            }
            return response;
          }),
        ),
    );
  }

  getAccountTypeName(id: number | undefined) {
    if (id === undefined) return undefined;
    return this.cachedAccountType.get(id);
  }

  updateTypeFilter(type: string) {
    if (type === "") {
      delete this.abstractAccountFilter.accountType;
    } else {
      this.abstractAccountFilter.accountType = Number(type);
    }
    this.resetSearch();
    this.getSearchResult();
  }

  onTypeFilterChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.updateTypeFilter(target.value);
  }

  override ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      if (params["member"] !== undefined) {
        this.abstractAccountFilter.member = +params["member"];
      }
      this.getSearchResult();
    });
    this.appConstantsService.getAccountTypes().subscribe((data) => {
      this.accountTypes = data;
    });
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
