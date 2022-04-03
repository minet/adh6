import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { SearchPage } from '../search-page';
import { Observable } from 'rxjs';
import { PaymentMethod, Transaction, TransactionService, AbstractTransaction } from '../api';
import { PagingConf } from '../paging.config';
import { map } from 'rxjs/operators';
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
export class TransactionListComponent extends SearchPage implements OnInit {
  @Input() asAccount: number;
  @Output() onAction: EventEmitter<{ name: string, transaction: Transaction }> = new EventEmitter<{ name; string, transaction: Transaction }>();
  @Input() refresh: EventEmitter<{ action: string }>;

  @Input() actions: Array<Action>;

  faClock = faClock;
  maxItems$: Observable<number>;
  result$: Observable<Array<Transaction>>;
  paymentMethods: Array<PaymentMethod>;

  filterType: string;

  constructor(public transactionService: TransactionService,
    public appConstantsService: AppConstantsService) {
    super();
  }

  updateTypeFilter(type: string) {
    this.filterType = type;
    this.loadData();
  }

  ngOnInit() {
    super.ngOnInit();
    this.loadData();
    this.appConstantsService.getPaymentMethods().subscribe(
      data => {
        this.paymentMethods = data;
      }
    );
    if (this.refresh) {
      this.refresh.subscribe((e: any) => {
        if (e.action === 'refresh') {
          this.loadData();
        }
      });
    }
  }

  loadData() {
    this.maxItems$ = this.getSearchHeader((terms) => this.fetchTransactionHead(terms));
    this.result$ = this.getSearchResult((terms, page) => this.fetchTransaction(terms, page));
  }

  private fetchTransactionHead(terms: string): Observable<number> {
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
    return this.transactionService.transactionHead(1, 0, terms, abstractTransaction, 'response')
      .pipe(map((response) => { return (response) ? +response.headers.get("x-total-count") : 0 }));
  }

  private fetchTransaction(terms: string, page: number): Observable<Array<Transaction>> {
    const n = +PagingConf.item_count;
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
    return this.transactionService.transactionGet(n, (page - 1) * n, terms, abstractTransaction);
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
