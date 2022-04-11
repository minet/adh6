import { Component, EventEmitter, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { filter, map, switchMap, takeWhile } from 'rxjs/operators';

import { Account, AccountService, PaymentMethod, Transaction, TransactionService } from '../../api';

import { faArrowUp, faExchangeAlt, faUndo, faCheck, faTrash, faClock } from '@fortawesome/free-solid-svg-icons';
import { ActivatedRoute } from '@angular/router';
import { AppConstantsService } from '../../app-constants.service';
import { NotificationService } from '../../notification.service';

export { ClickOutsideDirective } from '../clickOutside.directive';

export interface AccountListResult {
  accounts?: Array<Account>;
}

@Component({
  selector: 'app-transaction-new',
  templateUrl: './transaction-new.component.html',
  styleUrls: ['./transaction-new.component.css']
})
export class TransactionNewComponent implements OnInit {
  public transactionModal = false;
  transactionDetails: FormGroup;
  reverting = false;
  faExchangeAlt = faExchangeAlt;
  faClock = faClock;
  actions = [
    { name: 'replay', buttonText: '<i class=\'fas fa-arrow-up\'></i>', class: 'is-primary', buttonIcon: faArrowUp, condition: (transaction: Transaction) => !transaction.pendingValidation },
    { name: 'revert', buttonText: '<i class=\'fas fa-undo\'></i>', class: 'is-danger', buttonIcon: faUndo, condition: (transaction: Transaction) => !transaction.pendingValidation },
    { name: 'validate', buttonText: '<i class=\'fas fa-check\'></i>', class: 'is-success', buttonIcon: faCheck, condition: (transaction: Transaction) => transaction.pendingValidation },
    { name: 'delete', buttonText: '<i class=\'fas fa-trash\'></i>', class: 'is-danger', buttonIcon: faTrash, condition: (transaction: Transaction) => transaction.pendingValidation }
  ];
  paymentMethods: Array<PaymentMethod>;
  selectedSrcAccount: Account;
  selectedDstAccount: Account;
  refreshTransactions: EventEmitter<{ action: string }> = new EventEmitter();
  private alive = true;

  constructor(private fb: FormBuilder,
    public transactionService: TransactionService,
    public appConstantService: AppConstantsService,
    private accountService: AccountService,
    private notificationService: NotificationService,
    private route: ActivatedRoute) {
    this.createForm();
  }

  public toogleModal(): void {
    this.transactionModal = !this.transactionModal;
  }

  useTransaction(event: { name: string, transaction: Transaction }) {
    if (event.name === 'validate') {
      this.transactionService.validate(event.transaction.id)
        .pipe(takeWhile(() => this.alive))
        .subscribe((_) => {
          this.notificationService.successNotification('Ok!', 'Transaction validée avec succès !');
          this.refreshTransactions.next({ action: 'refresh' });
        });
    } else if (event.name === 'delete') {
      this.transactionService.transactionIdDelete(event.transaction.id)
        .pipe(takeWhile(() => this.alive))
        .subscribe((_) => {
          this.notificationService.successNotification('Ok!', 'Transaction supprimée avec succès !');
          this.refreshTransactions.next({ action: 'refresh' });
        });
    }
    this.transactionDetails.reset();
    this.transactionDetails.patchValue(event.transaction);
    if (event.name === 'revert') {
      this.selectedDstAccount = event.transaction.src as Account;
      this.selectedSrcAccount = event.transaction.dst as Account;
      this.transactionDetails.patchValue({ 'name': 'ANNULATION: ' + event.transaction.name });
      this.reverting = true;
    } else {
      this.selectedDstAccount = event.transaction.dst as Account;
      this.selectedSrcAccount = event.transaction.src as Account;
      this.reverting = false;
    }
    this.transactionDetails.patchValue({ 'paymentMethod': (event.transaction.paymentMethod as PaymentMethod).id });
  }

  getPaymentMethodNameById(id: number) {
    for (const pm of this.paymentMethods) {
      if (pm.id === id) {
        return pm.name;
      }
    }

    return 'Unknown';
  }

  exchangeAccounts() {
    const srcAccount = this.selectedSrcAccount;
    this.selectedSrcAccount = this.selectedDstAccount;
    this.selectedDstAccount = srcAccount;
  }

  isFormInvalid() {
    return this.selectedSrcAccount === undefined || this.selectedDstAccount === undefined;
  }

  get caisse(): string {
    return this.transactionDetails.get('caisse').value as string;
  }

  setCaisse(value: string): void {
    this.transactionDetails.patchValue({ 'caisse': value });
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
    this.route.params.pipe(
      map(params => params['account_id']),
      filter(id => id),
      switchMap(id => this.accountService.accountIdGet(id))
    ).subscribe(account => this.selectedSrcAccount = account);

    this.appConstantService.getPaymentMethods().subscribe(
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
      pendingValidation: (v.pending_validation == null) ? false : v.pending_validation
    };
    if (!varTransaction.cashbox) {
      varTransaction.cashbox = 'direct';
    }
    this.transactionService.transactionPost(varTransaction)
      .pipe(takeWhile(() => this.alive))
      .subscribe((_) => {
        this.transactionDetails.reset();
        this.notificationService.successNotification('Ok!', 'Transaction créée avec succès !');
        this.refreshTransactions.next({ action: 'refresh' });
      });
  }
}
