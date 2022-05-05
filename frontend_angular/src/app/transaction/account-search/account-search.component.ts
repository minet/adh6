import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import { map, of } from 'rxjs';
import { AccountService, Account } from '../../api';
import { SearchPage } from '../../search-page';

export { ClickOutsideDirective } from '../clickOutside.directive';

@Component({
  selector: 'app-account-search',
  templateUrl: './account-search.component.html',
  styleUrls: ['./account-search.component.sass']
})
export class AccountSearchComponent extends SearchPage<Account> implements OnInit {
  public display = false;

  @Input() selectedAccount: Account;
  @Output() accountSelected = new EventEmitter<Account>();

  constructor(
    private accountService: AccountService
  ) {
    super((terms: string, _) => this.accountService.accountGet(5, 0, terms, undefined, undefined, "response")
      .pipe(
        map((response) => {
          this.display = true;
          return response;
        })
      ), false);
  }

  ngOnInit(): void {
    super.ngOnInit();
    this.result$ = of(undefined);
  }

  search(terms: string): void {
    console.log(terms)
    super.search(terms);
    this.getSearchResult();
  }

  setSelectedAccount(account): void {
    this.result$ = undefined;
    this.selectedAccount = account;
    this.display = false;
    this.accountSelected.emit(this.selectedAccount);
  }
}
