import { Component, EventEmitter, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';

import { map, takeWhile } from 'rxjs/operators';

import { PaymentMethod, Transaction, TransactionService } from '../../api';

import { ActivatedRoute } from '@angular/router';
import { AppConstantsService } from '../../app-constants.service';
import { NotificationService } from '../../notification.service';

export { ClickOutsideDirective } from '../clickOutside.directive';

interface TransactionForm {
  name: FormControl<string>;
  value: FormControl<number>;
  srcAccount: FormControl<number>;
  dstAccount: FormControl<number>;
  paymentMethod: FormControl<number>;
  caisse: FormControl<Transaction.CashboxEnum>;
}

@Component({
  selector: 'app-transaction-new',
  templateUrl: './transaction-new.component.html'
})
export class TransactionNewComponent implements OnInit {
  public transactionModal = false;
  public transactionDetails: FormGroup<TransactionForm>;
  public reverting = false;
  actions = [
    { name: 'replay', class: 'is-primary', buttonIcon: 'refresh-arrow', condition: (transaction: Transaction) => !transaction.pendingValidation },
    { name: 'revert', class: 'is-danger', buttonIcon: 'repeat-arrow', condition: (transaction: Transaction) => !transaction.pendingValidation },
    { name: 'validate', class: 'is-success', buttonIcon: 'check', condition: (transaction: Transaction) => transaction.pendingValidation },
    { name: 'delete', class: 'is-danger', buttonIcon: 'trash-bin', condition: (transaction: Transaction) => transaction.pendingValidation }
  ];
  public paymentMethods: Array<PaymentMethod> = [];
  refreshTransactions: EventEmitter<{ action: string }> = new EventEmitter();
  private alive = true;

  public cashboxButtons: Array<{act: Transaction.CashboxEnum, text: string}> = [
    {act: Transaction.CashboxEnum.Direct, text: "Sans"},
    {act: Transaction.CashboxEnum.From, text: "Sortir"},
    {act: Transaction.CashboxEnum.To, text: "Ajouter"},
  ]

  constructor(
    private fb: FormBuilder,
    public transactionService: TransactionService,
    public appConstantService: AppConstantsService,
    private notificationService: NotificationService,
    private route: ActivatedRoute
  ) {
    this.transactionDetails = this.fb.group({
      name: ['', Validators.required],
      value: [0, Validators.required],
      srcAccount: [0, Validators.required],
      dstAccount: [0, Validators.required],
      paymentMethod: [0, Validators.required],
      caisse: [Transaction.CashboxEnum.Direct, Validators.required],
    });
  }

  ngOnInit() {
    this.route.params.pipe(
      map(params => params['account_id']),
    ).subscribe(account => this.transactionDetails.patchValue({ srcAccount: account.id }));
    this.appConstantService.getPaymentMethods().subscribe(
      data => {
        this.paymentMethods = data;
      }
    );
  }

  public toogleModal(): void {
    this.transactionModal = !this.transactionModal;
  }

  useTransaction(event: { name: string, transaction: Transaction }) {
    if (event.name === 'validate') {
      this.transactionService.validate(event.transaction.id ? event.transaction.id : 0)
        .pipe(takeWhile(() => this.alive))
        .subscribe((_) => {
          this.notificationService.successNotification('Ok!', 'Transaction validée avec succès !');
          this.refreshTransactions.next({ action: 'refresh' });
        });
    } else if (event.name === 'delete') {
      this.transactionService.transactionIdDelete(event.transaction.id ? event.transaction.id : 0)
        .pipe(takeWhile(() => this.alive))
        .subscribe((_) => {
          this.notificationService.successNotification('Ok!', 'Transaction supprimée avec succès !');
          this.refreshTransactions.next({ action: 'refresh' });
        });
    }
    this.transactionDetails.reset();
    this.transactionDetails.patchValue(event.transaction);
    this.reverting = event.name === 'revert'
    if (event.name === 'revert') {
      this.transactionDetails.patchValue({ dstAccount: event.transaction.src ? event.transaction.src : 0 });
      this.transactionDetails.patchValue({ srcAccount: event.transaction.dst ? event.transaction.dst : 0 });
      this.transactionDetails.patchValue({ name: 'ANNULATION: ' + event.transaction.name });
    } else {
      this.transactionDetails.patchValue({ srcAccount: event.transaction.src ? event.transaction.src : 0 });
      this.transactionDetails.patchValue({ dstAccount: event.transaction.dst ? event.transaction.dst : 0 });
    }
    this.transactionDetails.patchValue({ paymentMethod: event.transaction.paymentMethod });
  }

  getPaymentMethodNameById(id: number) {
    for (const pm of this.paymentMethods) {
      if (pm.id === id) {
        return pm.name;
      }
    }
    return 'Unknown';
  }

  exchangeAccounts(src: number, dst: number) {
    this.transactionDetails.patchValue({srcAccount: dst});
    this.transactionDetails.patchValue({dstAccount: src});
  }

  onSubmit() {
    const v = this.transactionDetails.value;
    this.transactionService.transactionPost({
      attachments: [],
      dst: v.dstAccount,
      name: v.name,
      src: v.srcAccount,
      paymentMethod: v.paymentMethod,
      value: v.value,
      cashbox: v.caisse,
    })
      .pipe(takeWhile(() => this.alive))
      .subscribe((_) => {
        this.transactionDetails.reset();
        this.notificationService.successNotification('Ok!', 'Transaction créée avec succès !');
        this.refreshTransactions.next({ action: 'refresh' });
      });
  }
}
