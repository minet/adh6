import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { SearchPage } from '../search-page';
import { Observable } from 'rxjs';
import { PaymentMethod, Transaction, TransactionService, AbstractTransaction } from '../api';
import { PagingConf } from '../paging.config';
import { map } from 'rxjs/operators';
import { IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AppConstantsService } from '../app-constants.service';
import { faClock } from '@fortawesome/free-solid-svg-icons';

export interface TransactionListResult {
  transactions?: Array<Transaction>;
  item_count?: number;
  current_page?: number;
  items_per_page?: number;
}

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

  result$: Observable<TransactionListResult>;
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
    this.result$ = this.getSearchResult((terms, page) => this.fetchTransaction(terms, page));
  }

  private fetchTransaction(terms: string, page: number): Observable<TransactionListResult> {
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
    return this.transactionService.transactionGet(n, (page - 1) * n, terms, abstractTransaction, 'response')
      .pipe(
        map((response) => {
          return <TransactionListResult>{
            transactions: response.body,
            item_count: +response.headers.get('x-total-count'),
            current_page: page,
            items_per_page: n,
          };
        }),
      );
  }

  handlePageChange(page: number) {
    this.changePage(page);
    this.result$ = this.getSearchResult((terms, page) => this.fetchTransaction(terms, page));
  }
}
