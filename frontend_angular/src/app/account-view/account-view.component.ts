import { Component, OnInit } from '@angular/core';
import { Observable, combineLatest } from "rxjs";
import {map, share, switchMap} from 'rxjs/operators';
import { AccountService } from '../api';
import { Account } from '../api';
import {ActivatedRoute, Router} from '@angular/router';

import {TransactionService} from '../api';
import {Transaction} from '../api';
import {PagingConf} from '../paging.config';

import {SearchPage} from '../search-page';
import {InlineResponse200} from '../api';

export interface TransactionListResult {
  transactions?: Array<Transaction>;
  item_count?: number;
  current_page?: number;
  items_per_page?: number;
}

@Component({
  selector: 'app-account-view',
  templateUrl: './account-view.component.html',
  styleUrls: ['./account-view.component.css']
})
export class AccountViewComponent extends SearchPage implements OnInit {
  account$: Observable<Account>;
  balance$: Observable<InlineResponse200>;

  result$: Observable<TransactionListResult>;
  private id$: Observable<number>;

  constructor(
    private accountService: AccountService,
    private transactionService: TransactionService,
    private route: ActivatedRoute,
  ) {
    super();
  }

  ngOnInit() {
    // id of the account
    this.id$ = this.route.params.pipe(
      map(params => params['accountID'])
    );

    // stream, which will emit the account id every time the page needs to be refreshed
    const refresh$ = combineLatest([this.id$])
      .pipe(
        map(([x]) => x),
      );
    this.account$ = refresh$.pipe(
      switchMap(id => this.accountService.accountAccountIdGet(''+id)),
      share()
    );

    this.result$ = refresh$.pipe(
      switchMap(account => <Observable<TransactionListResult>>this.getSearchResult((terms, page) => this.fetchTransaction(account, page) )),
      share(),
    );

    this.balance$ = refresh$.pipe(
      switchMap( id => this.accountService.accountAccountIdBalanceGet(''+id)),
      share()
    );
  }

  private fetchTransaction(account: number, page: number): Observable<TransactionListResult> {
    console.log(account);
    const n = +PagingConf.item_count;
    return this.transactionService.transactionGet(n, (page - 1) * n, undefined, account, 'response')
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

  goBack() {
    window.history.back();
  }
}
