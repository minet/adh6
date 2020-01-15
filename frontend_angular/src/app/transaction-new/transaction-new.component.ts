import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import {concat, EMPTY, from, merge, Observable, Subject} from 'rxjs';
import {share, takeWhile} from 'rxjs/operators';
import {debounceTime, distinctUntilChanged, map, mergeMap, scan, switchMap} from 'rxjs/operators';

import {TransactionService} from '../api/api/transaction.service';
import {Transaction} from '../api/model/transaction';
import {PagingConf} from '../paging.config';

import {SearchPage} from '../search-page';

import { PaymentMethod } from '../api/model/paymentMethod';
import { Account } from '../api/model/account';
import { AccountService } from '../api/api/account.service';
import { PaymentMethodService } from '../api/api/paymentMethod.service';
import {InlineResponse200} from '../api';

export {ClickOutsideDirective} from '../clickOutside.directive';

export interface TransactionListResult {
  transactions?: Array<Transaction>;
  item_count?: number;
  current_page?: number;
  items_per_page?: number;
}

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

  paymentMethods$: Observable<Array<PaymentMethod>>;
  result$: Observable<TransactionListResult>;

  srcSearchResult$: Observable<Array<Account>>;
  dstSearchResult$: Observable<Array<Account>>;

  selectedSrcAccountBalance$: Observable<InlineResponse200>;
  selectedDstAccountBalance$: Observable<InlineResponse200>;

  selectedSrcAccount: Account;
  selectedDstAccount: Account;


  constructor(private fb: FormBuilder,
  public transactionService: TransactionService,
  public paymentMethodService: PaymentMethodService,
  private accountService: AccountService) {
    super();
    this.createForm();
  }

  srcSearch(terms: string) {
    this.srcSearchResult$ = this.getSearchResult((x) => {
        return this.accountService.accountGet(20, 0, terms).pipe(
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
        return this.accountService.accountGet(20, 0, terms).pipe(
          map((response) => {
            this.displayDst = true;
            return <AccountListResult>{
              accounts: response
            };
          }),
        );
      });
  }

  setSelectedAccount(account, src) {
    if (src == true) {
      this.srcSearchResult$ = undefined;
      this.selectedSrcAccount = account;
      this.selectedSrcAccountBalance$ = this.accountService.accountAccountIdBalanceGet(account.id);
    } else {
      this.dstSearchResult$ = undefined;
      this.selectedDstAccount = account;
      this.selectedDstAccountBalance$ = this.accountService.accountAccountIdBalanceGet(account.id);
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
      srcAccount: ['', Validators.required],
      dstAccount: ['', Validators.required],
      paymentMethod: ['', Validators.required]
    });
  }

  ngOnInit() {
    super.ngOnInit();
    this.result$ = this.getSearchResult((terms, page) => this.fetchTransaction(terms, page));
    this.paymentMethods$ = this.paymentMethodService.paymentMethodGet();
  }

  private fetchTransaction(terms: string, page: number): Observable<TransactionListResult> {
    const n = +PagingConf.item_count;
    return this.transactionService.transactionGet(n, (page - 1) * n, terms, undefined, 'response')
      .pipe(
        map((response) => {
          return <TransactionListResult>{
            transactions: response.body,
            item_count: +response.headers.get('x-total-count'),
            current_page: page,
            items_per_page: n,
          };
        }),
      );

  }

  onSubmit() {
      const v = this.transactionDetails.value;
      const varTransaction: Transaction = {
        attachments: '',
        dstID: this.selectedDstAccount.id,
        name: v.name,
        srcID: this.selectedSrcAccount.id,
        paymentMethodID: +v.paymentMethod,
        value: v.value,
      };

    this.transactionService.transactionPost(varTransaction)
      .pipe(takeWhile(() => this.alive))
      .subscribe((res) => {
          this.result$ = this.getSearchResult((terms, page) => this.fetchTransaction(terms, page));
      });
  }
}
