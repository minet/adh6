import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import { map, of } from 'rxjs';
import { AccountService, AbstractAccount } from '../../api';
import { SearchPage } from '../../search-page';

export { ClickOutsideDirective } from '../clickOutside.directive';

@Component({
  selector: 'app-account-search',
  templateUrl: './account-search.component.html',
  styleUrls: ['./account-search.component.sass']
})
export class AccountSearchComponent extends SearchPage<AbstractAccount> implements OnInit {
  public display = false;
  public selectedAccount: AbstractAccount;
  @Input() inputAccountId: number | undefined;
  @Output() selectedAccountId = new EventEmitter<number>();

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
    if (this.inputAccountId) {
      this.accountService.accountIdGet(this.inputAccountId).subscribe(account => this.selectedAccount = account);
    }
    this.result$ = of(undefined);
  }

  search(terms: string): void {
    super.search(terms);
    this.getSearchResult();
  }

  setSelectedAccount(account: AbstractAccount): void {
    this.result$ = undefined;
    this.selectedAccount = account;
    this.display = false;
    this.selectedAccountId.emit(this.selectedAccount.id);
  }
}
