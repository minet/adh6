import { Component, EventEmitter, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { map, takeWhile } from 'rxjs/operators';

import { PaymentMethod, Transaction, TransactionService } from '../../api';

import { faArrowUp, faExchangeAlt, faUndo, faCheck, faTrash, faClock } from '@fortawesome/free-solid-svg-icons';
import { ActivatedRoute } from '@angular/router';
import { AppConstantsService } from '../../app-constants.service';
import { NotificationService } from '../../notification.service';

export { ClickOutsideDirective } from '../clickOutside.directive';

@Component({
  selector: 'app-transaction-new',
  templateUrl: './transaction-new.component.html',
  styleUrls: ['./transaction-new.component.css']
})
export class TransactionNewComponent implements OnInit {
  public transactionModal = false;
  public transactionDetails: FormGroup;
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
  refreshTransactions: EventEmitter<{ action: string }> = new EventEmitter();
  private alive = true;

  constructor(
    private fb: FormBuilder,
    public transactionService: TransactionService,
    public appConstantService: AppConstantsService,
    private notificationService: NotificationService,
    private route: ActivatedRoute
  ) {
    this.createForm();
  }

  ngOnInit() {
    this.route.params.pipe(
      map(params => params['account_id']),
    ).subscribe(account => this.srcAccount = account.id);
    this.appConstantService.getPaymentMethods().subscribe(
      data => {
        this.paymentMethods = data;
      }
    );
  }

  public toogleModal(): void {
    this.transactionModal = !this.transactionModal;
  }

  createForm() {
    this.transactionDetails = this.fb.group({
      name: ['', Validators.required],
      value: ['', Validators.required],
      srcAccount: ['', Validators.required],
      dstAccount: ['', Validators.required],
      paymentMethod: ['', Validators.required],
      caisse: ['direct'],
      pendingValidation: [false],
    });
  }

  get caisse(): string {
    return this.transactionDetails.get('caisse').value as string;
  }

  set caisse(value: string) {
    this.transactionDetails.patchValue({ 'caisse': value });
  }

  get srcAccount(): number {
    return this.transactionDetails.get("srcAccount").value as number
  }

  set srcAccount(account_id: number) {
    this.transactionDetails.patchValue({ 'srcAccount': account_id });
  }

  get dstAccount(): number {
    return this.transactionDetails.get("dstAccount").value as number
  }

  set dstAccount(account_id: number) {
    this.transactionDetails.patchValue({ 'dstAccount': account_id });
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
      this.dstAccount = event.transaction.src;
      this.srcAccount = event.transaction.dst;
      this.transactionDetails.patchValue({ 'name': 'ANNULATION: ' + event.transaction.name });
      this.reverting = true;
    } else {
      this.dstAccount = event.transaction.dst;
      this.srcAccount = event.transaction.src;
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
    const srcAccount = this.srcAccount;
    this.srcAccount = this.dstAccount;
    this.dstAccount = srcAccount;
  }

  onSubmit() {
    const v = this.transactionDetails.value;
    const varTransaction: Transaction = {
      attachments: [],
      dst: +v.dstAccount,
      name: v.name,
      src: +v.srcAccount,
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
