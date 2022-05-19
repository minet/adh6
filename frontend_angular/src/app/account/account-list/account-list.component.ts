import { Component, Input, OnInit } from '@angular/core';
import { Account, AccountService, AccountType } from '../../api';
import { SearchPage } from '../../search-page';
import { AbstractAccount } from '../../api/model/abstractAccount';
import { AppConstantsService } from '../../app-constants.service';

import { faThumbtack, faBan } from '@fortawesome/free-solid-svg-icons';
import { ActivatedRoute } from '@angular/router';
import { map, Observable, shareReplay } from 'rxjs';

@Component({
  selector: 'app-account-list',
  templateUrl: './account-list.component.html',
  styleUrls: ['./account-list.component.css']
})
export class AccountListComponent extends SearchPage<Account> implements OnInit {
  faThumbtack = faThumbtack;
  faBan = faBan;
  accountTypes: Array<AccountType>;
  @Input() abstractAccountFilter: AbstractAccount = {};
  cachedAccountType: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();

  constructor(
    private accountService: AccountService,
    private route: ActivatedRoute,
    private appConstantsService: AppConstantsService
  ) {
    super((terms, page) => this.accountService.accountGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, this.abstractAccountFilter, ["name", "balance", "actif", "accountType"], "response")
      .pipe(
        map(response => {
          for (let i of response.body) {
            if (i.accountType && !this.cachedAccountType.has(i.accountType)) {
              this.cachedAccountType.set(i.accountType, this.accountService.accountTypeIdGet(i.accountType).pipe(
                shareReplay(1),
                map(result => result.name)
              ));
            }
          }
          return response;
        })
      ));
  }

  getAccountTypeName(id: number) {
    return this.cachedAccountType.get(id);
  }

  updateTypeFilter(type: string) {
    if (type === '') { delete this.abstractAccountFilter.accountType; } else { this.abstractAccountFilter.accountType = Number(type); }
    this.getSearchResult();
  }

  ngOnInit() {
    this.route
      .queryParams
      .subscribe(params => {
        if (params['member'] !== undefined) {
          this.abstractAccountFilter.member = +params['member'];
          this.getSearchResult();
        }
      });
    this.getSearchResult();
    this.appConstantsService.getAccountTypes().subscribe(
      data => {
        this.accountTypes = data;
      }
    );
  }

  updateSearch() {
    this.getSearchResult();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
