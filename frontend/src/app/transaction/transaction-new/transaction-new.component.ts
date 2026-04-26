import {Component, EventEmitter, OnInit} from "@angular/core";
import {RouterModule} from "@angular/router";
import {CommonModule} from "@angular/common";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";

import {takeWhile} from "rxjs/operators";

import {PaymentMethod, Transaction, TransactionService} from "../../api";
import {TransactionListComponent} from "../../transaction-list/transaction-list.component";

import {AppConstantsService} from "../../app-constants.service";
import {NotificationService} from "../../notification.service";

export {ClickOutsideDirective} from "../clickOutside.directive";

interface TransactionForm {
  name: FormControl<string>;
  value: FormControl<number>;
  paymentMethod: FormControl<number>;
}

@Component({
  imports: [
    RouterModule,
    ReactiveFormsModule,
    CommonModule,
    TransactionListComponent,
  ],
  selector: "app-transaction-new",
  templateUrl: "./transaction-new.component.html",
  standalone: true,
})
export class TransactionNewComponent implements OnInit {
  public transactionDetails: FormGroup<TransactionForm>;
  public actions = [
    {
      name: "delete",
      class: "is-danger",
      buttonIcon: "trash-bin",
      condition: (_transaction: Transaction) => true,
    },
  ];
  public paymentMethods: PaymentMethod[] = [];
  refreshTransactions: EventEmitter<{action: string}> = new EventEmitter();
  private readonly alive = true;

  constructor(
    private readonly fb: FormBuilder,
    public transactionService: TransactionService,
    public appConstantService: AppConstantsService,
    private readonly notificationService: NotificationService,
  ) {
    this.transactionDetails = this.fb.group<TransactionForm>({
      name: this.fb.control("", {
        nonNullable: true,
        validators: [Validators.required],
      }),
      value: this.fb.control(0, {
        nonNullable: true,
        validators: [Validators.required, Validators.min(0)],
      }),
      paymentMethod: this.fb.control(0, {
        nonNullable: true,
        validators: [Validators.required, Validators.min(1)],
      }),
    });
  }

  ngOnInit() {
    this.appConstantService.getPaymentMethods().subscribe((data) => {
      this.paymentMethods = data;
    });
  }

  useTransaction(event: {name: string; transaction: Transaction}) {
    if (event.name === "delete") {
      this.transactionService
        .transactionIdDelete(event.transaction.id ?? 0)
        .pipe(takeWhile(() => this.alive))
        .subscribe(() => {
          this.notificationService.successNotification(
            "Ok!",
            "Transaction supprimée avec succès !",
          );
          this.refreshTransactions.next({action: "refresh"});
        });
    }
  }

  onSubmit() {
    const v = this.transactionDetails.value;

    if (!v.name || v.paymentMethod == null || v.value == null) {
      this.notificationService.errorNotification(
        400,
        "Form Error",
        "Please fill all required fields",
      );
      return;
    }

    this.transactionService
      .transactionPost({
        name: v.name,
        paymentMethod: +v.paymentMethod,
        value: v.value,
      })
      .pipe(takeWhile(() => this.alive))
      .subscribe(() => {
        this.transactionDetails.reset();
        this.notificationService.successNotification(
          "Ok!",
          "Transaction créée avec succès !",
        );
        this.refreshTransactions.next({action: "refresh"});
      });
  }
}
