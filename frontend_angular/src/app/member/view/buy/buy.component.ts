import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { Member, PaymentMethod, TransactionService } from '../../../api';

@Component({
  selector: 'app-buy',
  templateUrl: './buy.component.html',
  styleUrls: ['./buy.component.sass']
})
export class BuyComponent implements OnInit {
  @Input() member: Member;

  public paymentMethods$: Observable<PaymentMethod[]>;
  public amount: number = 0;
  public payment: number | undefined;

  public pay: number = 0;

  constructor(
    private transactionService: TransactionService,
  ) { }

  ngOnInit(): void {
    this.paymentMethods$ = this.transactionService.paymentMethodGet();
  }
}
