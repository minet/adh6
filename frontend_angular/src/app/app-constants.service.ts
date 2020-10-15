import {Injectable} from '@angular/core';
import {AccountService, AccountType, Member, MiscService, PaymentMethod, TransactionService} from './api';
import {Observable, of} from 'rxjs';
import {first, map, share} from 'rxjs/operators';
import {Ability, AbilityBuilder} from '@casl/ability';

@Injectable({
  providedIn: 'root'
})
export class AppConstantsService {

  private accountTypes: Array<AccountType>;
  private accountTypesObservable: Observable<any>;

  private paymentMethods: Array<PaymentMethod>;
  private paymentMethodsObservable: Observable<any>;

  private currentMember: Member;
  private currentMemberObservable: Observable<any>;

  constructor(public accountService: AccountService,
              public transactionService: TransactionService,
              private ability: Ability,
              public miscService: MiscService) {
  }

  getCurrentMember() {
    if (this.currentMember) {
      // if `data` is available just return it as `Observable`
      return of(this.currentMember);
    } else if (this.currentMemberObservable) {
      // if `this.observable` is set then the request is in progress
      // return the `Observable` for the ongoing request
      return this.currentMemberObservable;
    } else {
      this.currentMemberObservable = this.miscService.profile().pipe(
        map(profile => {
          const roles = profile.admin.roles;
          localStorage.setItem('roles', roles.join(','));
          localStorage.setItem('admin_member', JSON.stringify(profile.admin.member as Member));

          const { can, rules } = new AbilityBuilder();

          if (roles.indexOf('adh6_admin') !== -1) {
            can('manage', 'all');
          } else {
            can('manage', 'Member', { id: (profile.admin.member as Member).id });
            can('read', 'all');
          }

          // @ts-ignore
          this.ability.update(rules);

          this.currentMember = JSON.parse(localStorage.getItem('admin_member'));
          return this.currentMember;
        }),
        share()
      );
      return this.currentMemberObservable;
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
