import {Component, OnInit} from '@angular/core';
import {combineLatest, Observable} from 'rxjs';
import {map, share, switchMap} from 'rxjs/operators';
import {AbstractTransaction, Account, AccountService, AccountType, Transaction, TransactionService} from '../../api';
import {ActivatedRoute} from '@angular/router';
import {PagingConf} from '../../paging.config';

import {SearchPage} from '../../search-page';
import {AppConstantsService} from '../../app-constants.service';

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

  result$: Observable<TransactionListResult>;
  private id$: Observable<number>;
  accountTypes: Array<AccountType>;

  constructor(
    private accountService: AccountService,
    private transactionService: TransactionService,
    private route: ActivatedRoute,
    public appConstantsService: AppConstantsService
  ) {
    super();
  }

  ngOnInit() {
    // id of the account
    this.id$ = this.route.params.pipe(
      map(params => params['account_id'])
    );

    this.appConstantsService.getAccountTypes().subscribe(
      data => {
        this.accountTypes = data;
      }
    );
    // stream, which will emit the account id every time the page needs to be refreshed
    const refresh$ = combineLatest([this.id$])
      .pipe(
        map(([x]) => x),
      );
    this.account$ = refresh$.pipe(
      switchMap(id => this.accountService.accountAccountIdGet(id)),
      share()
    );

    this.result$ = refresh$.pipe(
      switchMap(account => <Observable<TransactionListResult>>this.getSearchResult((terms, page) => this.fetchTransaction(account, page) )),
      share(),
    );
  }

  goBack() {
    window.history.back();
  }

  private fetchTransaction(account: number, page: number): Observable<TransactionListResult> {
    console.log(account);
    const n = +PagingConf.item_count;

    const abstractTransaction: AbstractTransaction = {
      src: account,
      dst: account
    };

    return this.transactionService.transactionGet(n, (page - 1) * n, '', abstractTransaction, 'response')
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
