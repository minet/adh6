import {Injectable} from '@angular/core';
import {AccountService, AccountType, Member, MiscService, PaymentMethod, TransactionService} from './api';
import {Observable, of} from 'rxjs';
import {map, share} from 'rxjs/operators';
import {Ability, AbilityBuilder} from '@casl/ability';
import Swal from 'sweetalert2';

@Injectable({
  providedIn: 'root'
})
export class AppConstantsService {

  private accountTypes: Array<AccountType>;
  private accountTypesObservable: Observable<any>;

  private paymentMethods: Array<PaymentMethod>;
  private paymentMethodsObservable: Observable<any>;

  private currentMember: Member;
  private currentMember$: Observable<Member>;

  constructor(
    private accountService: AccountService,
    private transactionService: TransactionService,
    private miscService: MiscService,
  ) { }

  getCurrentMember(): Observable<Member> {
    if (this.currentMember) {
      // if `data` is available just return it as `Observable`
      return of(this.currentMember);
    } else if (this.currentMember$) {
      // if `this.observable` is set then the request is in progress
      // return the `Observable` for the ongoing request
      return this.currentMember$;
    } else {
      return this.miscService.profile().pipe(
        map(profile => {
          return profile.admin.member as Member;
        })
      );
    }
  }

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
