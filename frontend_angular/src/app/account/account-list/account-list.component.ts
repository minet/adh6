import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {Account, AccountService, AccountType} from '../../api';
import {SearchPage} from '../../search-page';
import {PagingConf} from '../../paging.config';
import {map} from 'rxjs/operators';
import {AbstractAccount} from '../../api/model/abstractAccount';
import {AppConstantsService} from '../../app-constants.service';

import {faThumbtack, faBan} from '@fortawesome/free-solid-svg-icons';
import {ActivatedRoute} from '@angular/router';

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
  faThumbtack = faThumbtack;
  faBan = faBan;

  result$: Observable<AccountListResponse>;
  accountTypes: Array<AccountType>;
  specificSearch = false;
  @Input() abstractAccountFilter: AbstractAccount = {};

  constructor(public accountService: AccountService,
              private route: ActivatedRoute,
              public appConstantsService: AppConstantsService) {
    super();
  }

  updateTypeFilter(type) {
    if (type === '') { delete this.abstractAccountFilter.accountType; } else { this.abstractAccountFilter.accountType = Number(type); }
    this.updateSearch();
  }

  updateSearch() {
    this.result$ = this.getSearchResult((terms, page) => this.fetchAccounts(terms, page));
  }

  ngOnInit() {
    this.route
      .queryParams
      .subscribe(params => {
        if (params['member'] !== undefined) {
          this.abstractAccountFilter.member = +params['member'];
          this.updateSearch();
        }
      });
    this.updateSearch();
    this.appConstantsService.getAccountTypes().subscribe(
      data => {
        this.accountTypes = data;
      }
    );
  }

  public updateBooleanFilter(property: any, trueValue: any, falseValue: any): any {
    if (this.abstractAccountFilter[property] === trueValue) {
      if (falseValue == null) {
        delete this.abstractAccountFilter[property];
      } else {
        this.abstractAccountFilter[property] = falseValue;
      }
    } else {
      this.abstractAccountFilter[property] = trueValue;
    }
    this.updateSearch();
  }

  private fetchAccounts(terms: string, page: number) {
    const n = +PagingConf.item_count;
    this.specificSearch = (terms !== '');

    return this.accountService.accountGet(n, (page - 1) * n, terms, this.abstractAccountFilter, 'response')
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
