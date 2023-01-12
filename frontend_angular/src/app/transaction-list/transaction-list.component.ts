import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { SearchPage } from '../search-page';
import { map, Observable, shareReplay } from 'rxjs';
import { PaymentMethod, Transaction, TransactionService, AbstractTransaction, AccountService, MemberService } from '../api';
import { AppConstantsService } from '../app-constants.service';
import { CommonModule } from '@angular/common';
import { PaginationComponent } from '../pagination/pagination.component';

class Action {
  name: string = "";
  buttonIcon: string = "";
  class: string = "";
  condition: any;
}

@Component({
  standalone: true,
  imports: [
    CommonModule,
    PaginationComponent
  ],
  selector: 'app-transaction-list',
  templateUrl: './transaction-list.component.html'
})
export class TransactionListComponent extends SearchPage<AbstractTransaction> implements OnInit {
  @Input() asAccount: number = 0;
  @Input() refresh: EventEmitter<{ action: string }> = new EventEmitter();
  @Input() actions: Array<Action> = [];

  @Output() whenOnAction: EventEmitter<{ name: string, transaction: Transaction }> = new EventEmitter();

  public result$: Observable<Array<Transaction>> = new Observable();
  public paymentMethods: Array<PaymentMethod> = [];
  public filterType: string = "";

  cachedAccountName: Map<Number, Observable<string>> = new Map();
  cachedPaymentMethodName: Map<Number, Observable<string>> = new Map();
  cachedMemberUsername: Map<Number, Observable<string>> = new Map();


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
    private transactionService: TransactionService,
    public appConstantsService: AppConstantsService,
    private accountService: AccountService,
    private memberService: MemberService,
  ) {
    super((terms, page) => {
      let abstractTransaction: AbstractTransaction = {};
      if (this.asAccount) {
        abstractTransaction = {
          src: this.asAccount,
          dst: this.asAccount
        };
      }
      if (this.filterType != null && this.filterType !== '') {
        abstractTransaction.paymentMethod = Number(this.filterType);
      }
      return this.transactionService.transactionGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, abstractTransaction, undefined, "response")
        .pipe(
          map(response => {
            response.body.forEach(i => {
              if (i.src && !this.cachedAccountName.has(i.src)) {
                this.cachedAccountName.set(i.src, this.accountService.accountIdGet(i.src).pipe(
                  shareReplay(1),
                  map(result => result.name || "")
                ));
              }
              if (i.dst && !this.cachedAccountName.has(i.dst)) {
                this.cachedAccountName.set(i.dst, this.accountService.accountIdGet(i.dst).pipe(
                  shareReplay(1),
                  map(result => result.name || "")
                ));
              }
              if (i.paymentMethod && !this.cachedPaymentMethodName.has(i.paymentMethod)) {
                this.cachedPaymentMethodName.set(i.paymentMethod, this.transactionService.paymentMethodIdGet(i.paymentMethod).pipe(
                  shareReplay(1),
                  map(result => result.name || "")
                ));
              }
              if (i.author && !this.cachedMemberUsername.has(i.author)) {
                this.cachedMemberUsername.set(i.author, this.memberService.memberIdGet(i.author, ["username"]).pipe(
                  shareReplay(1),
                  map(result => result.username || "")
                ));
              }
            })
            return response;
          })
        );
    });
  }

  updateTypeFilter(type: string) {
    this.filterType = type;
    this.getSearchResult();
  }

  ngOnInit() {
    super.ngOnInit();
    this.getSearchResult();
    this.appConstantsService.getPaymentMethods().subscribe(
      data => {
        this.paymentMethods = data;
      }
    );
    if (this.refresh) {
      this.refresh.subscribe((e: any) => {
        if (e.action === 'refresh') {
          this.getSearchResult();
        }
      });
    }
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
