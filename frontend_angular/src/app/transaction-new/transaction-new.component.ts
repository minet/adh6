import {Component, EventEmitter, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';

import {Observable} from 'rxjs';
import {filter, map, switchMap, takeWhile} from 'rxjs/operators';

import {Account, AccountService, PaymentMethod, Transaction, TransactionService} from '../api';

import {SearchPage} from '../search-page';
import {NotificationsService} from 'angular2-notifications';
import {faArrowUp, faExchangeAlt, faUndo, faCheck, faTrash, faClock} from '@fortawesome/free-solid-svg-icons';
import {ActivatedRoute} from '@angular/router';
import {AppConstantsService} from '../app-constants.service';

export {ClickOutsideDirective} from '../clickOutside.directive';

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
  displaySrc = false;
  displayDst = false;
  reverting = false;
  faExchangeAlt = faExchangeAlt;
  faClock = faClock;
  actions = [
    {name: 'replay', buttonText: '<i class=\'fas fa-arrow-up\'></i>', class: 'btn-primary', buttonIcon: faArrowUp, condition: (transaction) => !transaction.pendingValidation},
    {name: 'revert', buttonText: '<i class=\'fas fa-undo\'></i>', class: 'btn-danger', buttonIcon: faUndo, condition: (transaction) => !transaction.pendingValidation},
    {name: 'validate', buttonText: '<i class=\'fas fa-check\'></i>', class: 'btn-success', buttonIcon: faCheck, condition: (transaction) => transaction.pendingValidation},
    {name: 'delete', buttonText: '<i class=\'fas fa-trash\'></i>', class: 'btn-danger', buttonIcon: faTrash, condition: (transaction) => transaction.pendingValidation}
  ];
  paymentMethods: Array<PaymentMethod>;
  srcSearchResult$: Observable<Array<Account>>;
  dstSearchResult$: Observable<Array<Account>>;
  selectedSrcAccount: Account;
  selectedDstAccount: Account;
  refreshTransactions: EventEmitter<{ action: string }> = new EventEmitter();
  private alive = true;

  constructor(private fb: FormBuilder,
              public transactionService: TransactionService,
              private accountService: AccountService,
              public appConstantsService: AppConstantsService,
              private _service: NotificationsService,
              private route: ActivatedRoute) {
    super();
    this.createForm();
  }

  useTransaction(event: { name, transaction }) {
    if (event.name === 'validate') {
      this.transactionService.validate(event.transaction.id)
        .pipe(takeWhile(() => this.alive))
        .subscribe((res) => {
          this._service.success('Ok!', 'Transaction validée avec succès !');
          this.refreshTransactions.next({action: 'refresh'});
        });
    } else if (event.name === 'delete') {
      this.transactionService.transactionTransactionIdDelete(event.transaction.id)
        .pipe(takeWhile(() => this.alive))
        .subscribe((res) => {
          this._service.success('Ok!', 'Transaction supprimée avec succès !');
          this.refreshTransactions.next({action: 'refresh'});
        });
    }
    this.transactionDetails.reset();
    let source = true;
    if (event.name === 'revert') {
      source = false;
      this.reverting = true;
    } else {
      this.reverting = false;
    }
    this.setSelectedAccount(event.transaction.src, source);
    this.setSelectedAccount(event.transaction.dst, !source);
    this.transactionDetails.patchValue(event.transaction);
    if (event.name === 'revert') {
      this.transactionDetails.patchValue({'name': 'ANNULATION: ' + event.transaction.name});
    }
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

  getPaymentMethodNameById(id: number) {
    for (const pm of this.paymentMethods) {
      if (pm.id === id) {
        return pm.name;
      }
    }

    return 'Unknown';
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
    if (src === true) {
      this.srcSearchResult$ = undefined;
      this.selectedSrcAccount = account;
    } else {
      this.dstSearchResult$ = undefined;
      this.selectedDstAccount = account;
    }
    this.displayDst = false;
    this.displaySrc = false;
  }

  isFormInvalid() {
    return this.selectedSrcAccount === undefined || this.selectedDstAccount === undefined;
  }

  createForm() {
    this.transactionDetails = this.fb.group({
      name: ['', Validators.required],
      value: ['', Validators.required],
      srcAccount: [''],
      dstAccount: [''],
      paymentMethod: ['', Validators.required],
      caisse: ['direct'],
      pending_validation: [false],
    });
  }

  ngOnInit() {
    super.ngOnInit();

    this.route.params.pipe(
      map(params => params['account_id']),
      filter(id => id),
      switchMap(id => this.accountService.accountAccountIdGet(id))
    ).subscribe(
      account => this.setSelectedAccount(account, true)
    );

    this.appConstantsService.getPaymentMethods().subscribe(
      data => {
        this.paymentMethods = data;
      }
    );
  }

  onSubmit() {
    const v = this.transactionDetails.value;
    const varTransaction: Transaction = {
      attachments: [],
      dst: this.selectedDstAccount.id,
      name: v.name,
      src: this.selectedSrcAccount.id,
      paymentMethod: +v.paymentMethod,
      value: +v.value,
      cashbox: v.caisse,
      pendingValidation: v.pending_validation
    };
    if (!varTransaction.cashbox) {
      varTransaction.cashbox = 'direct';
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
