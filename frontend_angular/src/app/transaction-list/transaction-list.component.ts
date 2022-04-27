import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { SearchPage } from '../search-page';
import { Observable } from 'rxjs';
import { PaymentMethod, Transaction, TransactionService, AbstractTransaction } from '../api';
import { IconDefinition } from '@fortawesome/free-solid-svg-icons';
import { AppConstantsService } from '../app-constants.service';
import { faClock } from '@fortawesome/free-solid-svg-icons';

class Action {
  name: string;
  buttonText: string;
  buttonIcon: IconDefinition;
  class: string;
  condition: any;
}

@Component({
  selector: 'app-transaction-list',
  templateUrl: './transaction-list.component.html',
  styleUrls: ['./transaction-list.component.css']
})
export class TransactionListComponent extends SearchPage<Transaction> implements OnInit {
  @Input() asAccount: number;
  @Output() whenOnAction: EventEmitter<{ name: string, transaction: Transaction }> = new EventEmitter<{ name; string, transaction: Transaction }>();
  @Input() refresh: EventEmitter<{ action: string }>;

  @Input() actions: Array<Action>;

  faClock = faClock;
  result$: Observable<Array<Transaction>>;
  paymentMethods: Array<PaymentMethod>;

  filterType: string;

  constructor(public transactionService: TransactionService,
    public appConstantsService: AppConstantsService) {
    super((terms, page) => {
      let abstractTransaction: AbstractTransaction = {};
      if (this.asAccount) {
        abstractTransaction = {
          src: this.asAccount,
          dst: this.asAccount
        };
      }
      if (this.filterType != null && this.filterType !== '') {
        abstractTransaction.paymentMethod = Number(this.filterType);
      }
      return this.transactionService.transactionGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, abstractTransaction, "response");
    });
  }

  updateTypeFilter(type: string) {
    this.filterType = type;
    this.getSearchResult();
  }

  ngOnInit() {
    super.ngOnInit();
    this.getSearchResult();
    this.appConstantsService.getPaymentMethods().subscribe(
      data => {
        this.paymentMethods = data;
      }
    );
    if (this.refresh) {
      this.refresh.subscribe((e: any) => {
        if (e.action === 'refresh') {
          this.getSearchResult();
        }
      });
    }
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
