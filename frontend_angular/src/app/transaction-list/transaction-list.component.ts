import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {SearchPage} from '../search-page';
import {Observable} from 'rxjs';
import {MemberService, Transaction, TransactionService} from '../api';
import {PagingConf} from '../paging.config';
import {map} from 'rxjs/operators';

export interface TransactionListResult {
  transactions?: Array<Transaction>;
  item_count?: number;
  current_page?: number;
  items_per_page?: number;
}

@Component({
  selector: 'app-transaction-list',
  templateUrl: './transaction-list.component.html',
  styleUrls: ['./transaction-list.component.css']
})
export class TransactionListComponent extends SearchPage implements OnInit {
  @Input() asAccount: number;
  @Input() refresh: EventEmitter<{action: string}>;

  result$: Observable<TransactionListResult>;

  constructor(public transactionService: TransactionService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.loadData();
    this.refresh.subscribe((e: any) => {
      if (e.action === 'refresh') {
        this.loadData();
      }
    });
  }

  loadData() {
    this.result$ = this.getSearchResult((terms, page) => this.fetchTransaction(terms, page));
  }

  private fetchTransaction(terms: string, page: number): Observable<TransactionListResult> {
    const n = +PagingConf.item_count;
    return this.transactionService.transactionGet(n, (page - 1) * n, terms, this.asAccount, 'response')
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

}
