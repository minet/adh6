import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {Account, AccountService, AccountType} from '../api';
import {SearchPage} from '../search-page';
import {PagingConf} from '../paging.config';
import {map} from 'rxjs/operators';
import {AbstractAccount} from '../api/model/abstractAccount';
import {AppConstantsService} from '../app-constants.service';

import {faThumbtack} from '@fortawesome/free-solid-svg-icons';

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
  @Input() pinned = false;
  @Input() cav = false;

  faThumbtack = faThumbtack;

  result$: Observable<AccountListResponse>;
  accountTypes: Array<AccountType>;
  specificSearch = false;
  filterType: string;

  constructor(public accountService: AccountService,
              public appConstantsService: AppConstantsService) {
    super();
  }

  updateTypeFilter(type) {
    this.filterType = type;
    this.updateSearch();
  }
  updateSearch() {
    this.result$ = this.getSearchResult((terms, page) => this.fetchAccounts(terms, page));
  }

  ngOnInit() {
    this.updateSearch();
    this.appConstantsService.getAccountTypes().subscribe(
      data => {
        this.accountTypes = data;
      }
    );
  }

  private fetchAccounts(terms: string, page: number) {
    const n = +PagingConf.item_count;
    this.specificSearch = (terms !== '');

    const abstractAccount: AbstractAccount = {};

    if (this.pinned) {
      abstractAccount.pinned = true;
    }
    if (this.cav) {
      abstractAccount.compteCourant = true;
    }
    if (this.filterType != null && this.filterType !== '') {
      abstractAccount.accountType = Number(this.filterType);
    }

    return this.accountService.accountGet(n, (page - 1) * n, terms, abstractAccount, 'response')
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
