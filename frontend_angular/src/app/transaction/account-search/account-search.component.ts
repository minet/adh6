import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import { map, Observable } from 'rxjs';
import { AccountService, Account } from '../../api';
import { SearchPage } from '../../search-page';

export { ClickOutsideDirective } from '../clickOutside.directive';

export interface AccountListResult {
  accounts?: Array<Account>;
}

@Component({
  selector: 'app-account-search',
  templateUrl: './account-search.component.html',
  styleUrls: ['./account-search.component.sass']
})
export class AccountSearchComponent extends SearchPage implements OnInit {
  accountSearchResult$: Observable<Array<Account>>;
  public display = false;

  @Input() selectedAccount: Account;
  @Output() accountSelected = new EventEmitter<Account>();

  constructor(
    private accountService: AccountService
  ) {
    super();
  }

  ngOnInit(): void {
  }
  srcSearch(terms: string) {
    this.accountSearchResult$ = this.getSearchResult((_) => {
      return this.accountService.accountGet(5, 0, terms).pipe(
        map((response) => {
          this.display = true;
          return <AccountListResult>{
            accounts: response
          };
        }),
      );
    });
  }
  setSelectedAccount(account): void {
    this.accountSearchResult$ = undefined;
    this.selectedAccount = account;
    this.display = false;
    this.accountSelected.emit(this.selectedAccount);
  }
}
