import { Injectable } from '@angular/core';
import { AccountService, AccountType, PaymentMethod, TransactionService } from './api';
import { Observable, of } from 'rxjs';
import { map, share } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AppConstantsService {

  private accountTypes: Array<AccountType>;
  private accountTypesObservable: Observable<any>;

  private paymentMethods: Array<PaymentMethod>;
  private paymentMethodsObservable: Observable<any>;

  constructor(
    private accountService: AccountService,
    private transactionService: TransactionService,
  ) { }

  getPaymentMethods() {
    if (this.paymentMethods) {
      // if `data` is available just return it as `Observable`
      return of(this.paymentMethods);
    } else if (this.paymentMethodsObservable) {
      // if `this.observable` is set then the request is in progress
      // return the `Observable` for the ongoing request
      return this.paymentMethodsObservable;
    } else {
      this.paymentMethodsObservable = this.transactionService.paymentMethodGet().pipe(
        map(data => {
          // when the cached data is available we don't need the `Observable` reference anymore
          this.paymentMethodsObservable = null;
          this.paymentMethods = data;
          return this.paymentMethods;
        }),
        share()
      );
      return this.paymentMethodsObservable;
    }
  }

  getAccountTypes() {
    if (this.accountTypes) {
      // if `data` is available just return it as `Observable`
      return of(this.accountTypes);
    } else if (this.accountTypesObservable) {
      // if `this.observable` is set then the request is in progress
      // return the `Observable` for the ongoing request
      return this.accountTypesObservable;
    } else {
      this.accountTypesObservable = this.accountService.accountTypeGet().pipe(
        map(data => {
          // when the cached data is available we don't need the `Observable` reference anymore
          this.accountTypesObservable = null;
          this.accountTypes = data;
          return this.accountTypes;
        }),
        share()
      );
      return this.accountTypesObservable;
    }
  }
}
