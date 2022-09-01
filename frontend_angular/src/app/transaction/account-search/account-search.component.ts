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
  private _inputAccountId: number | undefined;

  @Input() set inputAccountId(value: number | undefined) {
    this._inputAccountId = value;
    if (value) {
      this.accountService.accountIdGet(this._inputAccountId).subscribe(account => this.selectedAccount = account);
    }
  }
  get inputAccountId(): number | undefined {
    return this._inputAccountId
  };

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
