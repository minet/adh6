import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { SearchPage } from '../search-page';
import { map, Observable, shareReplay } from 'rxjs';
import { PaymentMethod, Transaction, TransactionService, AbstractTransaction, AccountService, MemberService } from '../api';
import { IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AppConstantsService } from '../app-constants.service';
import { faClock } from '@fortawesome/free-solid-svg-icons';

class Action {
  name: string;
  buttonText: string;
  buttonIcon: IconDefinition;
  class: string;
  condition: any;
}

@Component({
  selector: 'app-transaction-list',
  templateUrl: './transaction-list.component.html',
  styleUrls: ['./transaction-list.component.css']
})
export class TransactionListComponent extends SearchPage<Transaction> implements OnInit {
  @Input() asAccount: number;
  @Output() whenOnAction: EventEmitter<{ name: string, transaction: Transaction }> = new EventEmitter<{ name; string, transaction: Transaction }>();
  @Input() refresh: EventEmitter<{ action: string }>;

  @Input() actions: Array<Action>;

  faClock = faClock;
  result$: Observable<Array<Transaction>>;
  paymentMethods: Array<PaymentMethod>;

  filterType: string;

  cachedAccountName: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();
  cachedPaymentMethodName: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();
  cachedMemberUsername: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();


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
      return this.transactionService.transactionGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, abstractTransaction, "response")
        .pipe(
          map(response => {
            for (let i of response.body) {
              if (i.src && !this.cachedAccountName.has(i.src)) {
                this.cachedAccountName.set(i.src, this.accountService.accountIdGet(i.src).pipe(
                  shareReplay(1),
                  map(result => result.name)
                ));
              }
              if (i.dst && !this.cachedAccountName.has(i.dst)) {
                this.cachedAccountName.set(i.dst, this.accountService.accountIdGet(i.dst).pipe(
                  shareReplay(1),
                  map(result => result.name)
                ));
              }
              if (i.paymentMethod && !this.cachedPaymentMethodName.has(i.paymentMethod)) {
                this.cachedPaymentMethodName.set(i.paymentMethod, this.transactionService.paymentMethodIdGet(i.paymentMethod).pipe(
                  shareReplay(1),
                  map(result => result.name)
                ));
              }
              if (i.author && !this.cachedMemberUsername.has(i.author)) {
                this.cachedMemberUsername.set(i.author, this.memberService.memberIdGet(i.author).pipe(
                  shareReplay(1),
                  map(result => result.username)
                ));
              }
            }
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
