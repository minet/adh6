import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { Observable } from 'rxjs';
import { Member, MembershipService, PaymentMethod, TransactionService } from '../../../api';
import { NotificationService } from '../../../notification.service';

@Component({
  selector: 'app-buy',
  templateUrl: './buy.component.html',
  styleUrls: ['./buy.component.sass']
})
export class BuyComponent implements OnInit {
  @Input() member: Member;
  @Output() updateSubscription = new EventEmitter<boolean>();

  public productCollapse: boolean = false;
  public membershipCollapse: boolean = false;

  public paymentMethods$: Observable<PaymentMethod[]>;
  public amount: number = 0;
  public payment: number | undefined;

  public pay: number = 0;
  public isFree: boolean = false;

  constructor(
    private transactionService: TransactionService,
    private membershipService: MembershipService,
    private notificationService: NotificationService
  ) { }

  ngOnInit(): void {
    this.paymentMethods$ = this.transactionService.paymentMethodGet();
  }

  public validatePayment(): void {
    this.membershipService.subscriptionValidate(this.member.id, (this.isFree) ? this.isFree : undefined).subscribe(() => {
      this.notificationService.successNotification(
        "Inscription finie",
        "L'inscription pour cet adhérent est finie"
      );
      this.subscriptionUpdated();
    }).unsubscribe();
  }

  public subscriptionUpdated() {
    this.updateSubscription.emit(true);
    this.membershipCollapse = false;
  }
}
