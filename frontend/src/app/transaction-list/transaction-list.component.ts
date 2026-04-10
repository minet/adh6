import {Component, EventEmitter, Input, OnInit, Output} from "@angular/core";
import {SearchPage} from "../search-page";
import {map, Observable, shareReplay} from "rxjs";
import {
  PaymentMethod,
  Transaction,
  TransactionService,
  AbstractTransaction,
  AccountService,
  MemberService,
} from "../api";
import {AppConstantsService} from "../app-constants.service";
import {CommonModule} from "@angular/common";
import {PaginationComponent} from "../pagination/pagination.component";

class Action {
  name = "";
  buttonIcon = "";
  class = "";
  condition: (transaction: Transaction) => boolean = () => true;
}

@Component({
  imports: [CommonModule, PaginationComponent],
  selector: "app-transaction-list",
  templateUrl: "./transaction-list.component.html",
})
export class TransactionListComponent
  extends SearchPage<AbstractTransaction>
  implements OnInit
{
  @Input() asAccount: number | undefined = 0;
  @Input() refresh: EventEmitter<{action: string}> = new EventEmitter();
  @Input() actions: Action[] = [];

  @Output() whenOnAction: EventEmitter<{
    name: string;
    transaction: Transaction;
  }> = new EventEmitter<{
    name: string;
    transaction: Transaction;
  }>();

  public override result$: Observable<Transaction[]> = new Observable();
  public paymentMethods: PaymentMethod[] = [];
  public filterType = "";

  cachedAccountName: Map<number, Observable<string>> = new Map();
  cachedPaymentMethodName: Map<number, Observable<string>> = new Map();
  cachedMemberUsername: Map<number, Observable<string>> = new Map();

  getUsername(id: number) {
    return this.cachedMemberUsername.get(id);
  }

  getAccountName(id: number) {
    return this.cachedAccountName.get(id);
  }

  getPaymentMethodName(id: number) {
    return this.cachedPaymentMethodName.get(id);
  }

  constructor(
    private readonly transactionService: TransactionService,
    public appConstantsService: AppConstantsService,
    private readonly accountService: AccountService,
    private readonly memberService: MemberService,
  ) {
    super((terms, page) => {
      let abstractTransaction: AbstractTransaction = {};
      if (this.asAccount) {
        abstractTransaction = {
          src: this.asAccount,
          dst: this.asAccount,
        };
      }
      if (this.filterType != null && this.filterType !== "") {
        abstractTransaction.paymentMethod = Number(this.filterType);
      }
      return this.transactionService
        .transactionGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          terms,
          abstractTransaction,
          undefined,
          "response",
        )
        .pipe(
          map((response) => {
            if (!response.body) {
              return response;
            }
            for (const i of response.body) {
              if (i.src && !this.cachedAccountName.has(i.src)) {
                this.cachedAccountName.set(
                  i.src,
                  this.accountService.accountIdGet(i.src).pipe(
                    shareReplay(1),
                    map((result) => result.name || ""),
                  ),
                );
              }
              if (i.dst && !this.cachedAccountName.has(i.dst)) {
                this.cachedAccountName.set(
                  i.dst,
                  this.accountService.accountIdGet(i.dst).pipe(
                    shareReplay(1),
                    map((result) => result.name || ""),
                  ),
                );
              }
              if (
                i.paymentMethod &&
                !this.cachedPaymentMethodName.has(i.paymentMethod)
              ) {
                this.cachedPaymentMethodName.set(
                  i.paymentMethod,
                  this.transactionService
                    .paymentMethodIdGet(i.paymentMethod)
                    .pipe(
                      shareReplay(1),
                      map((result) => result.name || ""),
                    ),
                );
              }
              if (i.author && !this.cachedMemberUsername.has(i.author)) {
                this.cachedMemberUsername.set(
                  i.author,
                  this.memberService.memberIdGet(i.author, ["username"]).pipe(
                    shareReplay(1),
                    map((result) => result.username || ""),
                  ),
                );
              }
            }
            return response;
          }),
        );
    });
  }

  updateTypeFilter(type: string) {
    this.filterType = type;
    this.getSearchResult();
  }

  onTypeFilterChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.updateTypeFilter(target.value);
  }

  override ngOnInit() {
    super.ngOnInit();
    this.getSearchResult();
    this.appConstantsService.getPaymentMethods().subscribe((data) => {
      this.paymentMethods = data;
    });
    if (this.refresh) {
      this.refresh.subscribe((e: {action: string}) => {
        if (e.action === "refresh") {
          this.getSearchResult();
        }
      });
    }
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
