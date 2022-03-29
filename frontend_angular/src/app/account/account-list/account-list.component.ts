import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { Account, AccountService, AccountType } from '../../api';
import { SearchPage } from '../../search-page';
import { PagingConf } from '../../paging.config';
import { map } from 'rxjs/operators';
import { AbstractAccount } from '../../api/model/abstractAccount';
import { AppConstantsService } from '../../app-constants.service';

import { faThumbtack, faBan } from '@fortawesome/free-solid-svg-icons';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-account-list',
  templateUrl: './account-list.component.html',
  styleUrls: ['./account-list.component.css']
})
export class AccountListComponent extends SearchPage implements OnInit {
  faThumbtack = faThumbtack;
  faBan = faBan;

  result$: Observable<Array<Account>>;
  maxItems$: Observable<number>;
  accountTypes: Array<AccountType>;
  specificSearch = false;
  @Input() abstractAccountFilter: AbstractAccount = {};

  constructor(
    private accountService: AccountService,
    private route: ActivatedRoute,
    private appConstantsService: AppConstantsService
  ) {
    super();
  }

  updateTypeFilter(type: string) {
    if (type === '') { delete this.abstractAccountFilter.accountType; } else { this.abstractAccountFilter.accountType = Number(type); }
    this.updateSearch();
  }

  updateSearch() {
    this.result$ = this.getSearchResult((terms, page) => this.fetchAccounts(terms, page));
    this.maxItems$ = this.getSearchHeader((terms) => this.accountService.accountHead(1, 0, terms, this.abstractAccountFilter, 'response').pipe(map((response) => { return (response) ? +response.headers.get("x-total-count") : 0 })));
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

    return this.accountService.accountGet(n, (page - 1) * n, terms, this.abstractAccountFilter)
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
