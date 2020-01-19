import {Component, EventEmitter, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';

import {Observable} from 'rxjs';
import {filter, map, switchMap, takeWhile} from 'rxjs/operators';

import {TransactionPatchRequest, TransactionService} from '../api';
import {Transaction} from '../api';

import {SearchPage} from '../search-page';

import {PaymentMethod} from '../api';
import {Account} from '../api';
import {AccountService} from '../api';
import {PaymentMethodService} from '../api';
import {InlineResponse200} from '../api';
import {NotificationsService} from 'angular2-notifications';

export {ClickOutsideDirective} from '../clickOutside.directive';

import {faArrowUp, faTrash, faExchangeAlt} from '@fortawesome/free-solid-svg-icons';
import {ActivatedRoute} from '@angular/router';

export interface AccountListResult {
  accounts?: Array<Account>;
}

@Component({
  selector: 'app-transaction-new',
  templateUrl: './transaction-new.component.html',
  styleUrls: ['./transaction-new.component.css']
})
export class TransactionNewComponent extends SearchPage implements OnInit {
  transactionDetails: FormGroup;
  private alive = true;
  displaySrc = false;
  displayDst = false;

  faExchangeAlt = faExchangeAlt;
  actions = [
    {name: 'replay', buttonText: '<i class=\'fas fa-arrow-up\'></i>', class: 'btn-primary', buttonIcon: faArrowUp},
    {name: 'reverse', buttonText: '<i class=\'fas fa-undo\'></i>', class: 'btn-danger', buttonIcon: faTrash}
  ];
  cashPaymentMethodID;

  paymentMethods$: Observable<Array<PaymentMethod>>;

  srcSearchResult$: Observable<Array<Account>>;
  dstSearchResult$: Observable<Array<Account>>;

  selectedSrcAccountBalance$: Observable<InlineResponse200>;
  selectedDstAccountBalance$: Observable<InlineResponse200>;

  selectedSrcAccount: Account;
  selectedDstAccount: Account;

  refreshTransactions: EventEmitter<{ action: string }> = new EventEmitter();


  constructor(private fb: FormBuilder,
              public transactionService: TransactionService,
              public paymentMethodService: PaymentMethodService,
              private accountService: AccountService,
              private _service: NotificationsService,
              private route: ActivatedRoute) {
    super();
    this.createForm();
  }

  useTransaction(event: { name, transaction }) {
    this.transactionDetails.reset();
    let source = true;
    if (event.name === 'reverse') {
      source = false;
    }
    this.setSelectedAccount(event.transaction.src, source);
    this.setSelectedAccount(event.transaction.dst, !source);
    this.transactionDetails.patchValue(event.transaction);
    this.transactionDetails.patchValue({'paymentMethod': event.transaction.paymentMethod.id});
  }

  srcSearch(terms: string) {
    this.srcSearchResult$ = this.getSearchResult((x) => {
      return this.accountService.accountGet(5, 0, terms).pipe(
        map((response) => {
          this.displaySrc = true;
          return <AccountListResult>{
            accounts: response
          };
        }),
      );
    });
  }

  dstSearch(terms: string) {
    this.dstSearchResult$ = this.getSearchResult((x) => {
      return this.accountService.accountGet(5, 0, terms).pipe(
        map((response) => {
          this.displayDst = true;
          return <AccountListResult>{
            accounts: response
          };
        }),
      );
    });
  }

  exchangeAccounts() {
    const srcAccount = this.selectedSrcAccount;
    this.setSelectedAccount(this.selectedDstAccount, true);
    this.setSelectedAccount(srcAccount, false);
  }

  setSelectedAccount(account, src) {
    if (src == true) {
      this.srcSearchResult$ = undefined;
      this.selectedSrcAccount = account;
      if (this.selectedSrcAccount) { this.selectedSrcAccountBalance$ = this.accountService.accountAccountIdBalanceGet(account.id); }
    } else {
      this.dstSearchResult$ = undefined;
      this.selectedDstAccount = account;
      if (this.selectedDstAccount) { this.selectedDstAccountBalance$ = this.accountService.accountAccountIdBalanceGet(account.id); }
    }
    this.displayDst = false;
    this.displaySrc = false;
  }

  isFormInvalid() {
    return this.selectedSrcAccount == undefined || this.selectedDstAccount == undefined;
  }

  createForm() {
    this.transactionDetails = this.fb.group({
      name: ['', Validators.required],
      value: ['', Validators.required],
      srcAccount: [''],
      dstAccount: [''],
      paymentMethod: ['', Validators.required],
      caisse: 'direct',
    });
  }

  ngOnInit() {
    super.ngOnInit();

    this.route.params.pipe(
      map(params => params['accountID']),
      filter(id => id),
      switchMap(id => this.accountService.accountAccountIdGet(id))
    ).subscribe(
      account => this.setSelectedAccount(account, true)
    );

    this.paymentMethods$ = this.paymentMethodService.paymentMethodGet();
    const that = this;
    this.paymentMethods$.subscribe(
      pm => pm.forEach(function (value) {
        if (value.name === 'Liquide') {
          that.cashPaymentMethodID = value.id;
        }
      }),
    );
  }

  onSubmit() {
    const v = this.transactionDetails.value;
    const varTransaction: TransactionPatchRequest = {
      attachments: '',
      dst: this.selectedDstAccount.id,
      name: v.name,
      src: this.selectedSrcAccount.id,
      paymentMethod: +v.paymentMethod,
      value: v.value,
      caisse: v.caisse
    };
    if (!varTransaction.caisse) {
      varTransaction.caisse = 'direct';
    }
    this.transactionService.transactionPost(varTransaction)
      .pipe(takeWhile(() => this.alive))
      .subscribe((res) => {
        this.transactionDetails.reset();
        this._service.success('Ok!', 'Transaction créée avec succès !');
        this.refreshTransactions.next({action: 'refresh'});
      });
  }
}
