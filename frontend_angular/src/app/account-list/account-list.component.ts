import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {Account, AccountService, AccountType, AccountTypeService, InlineResponse200} from '../api';
import {SearchPage} from '../search-page';
import {PagingConf} from '../paging.config';
import {map} from 'rxjs/operators';

class AccountListResponse {
  accounts?: Array<Account>;
  page_number?: number;
  item_count?: number;
  item_per_page?: number;
}


@Component({
  selector: 'app-account-list',
  templateUrl: './account-list.component.html',
  styleUrls: ['./account-list.component.css']
})
export class AccountListComponent extends SearchPage implements OnInit {
  @Input() filter: any;

  result$: Observable<AccountListResponse>;
  accountTypes: Array<AccountType>;

  constructor(public accountService: AccountService,
              public accountTypeService: AccountTypeService) {
    super();
  }

  ngOnInit() {
    this.result$ = this.getSearchResult((terms, page) => this.fetchAccounts(terms, page));

    this.accountTypeService.accountTypeGet()
      .subscribe(
        data => {
          this.accountTypes = data;
        }
      );
  }

  private fetchAccounts(terms: string, page: number) {
    const n = +PagingConf.item_count;
    return this.accountService.accountGet(n, (page - 1) * n, terms, undefined, undefined, 'response')
      .pipe(
        // switch to new search observable each time the term changes
        map((response) => <AccountListResponse>{
          accounts: response.body,
          item_count: +response.headers.get('x-total-count'),
          page_number: page,
          item_per_page: n,
        }),
      );
  }
}
