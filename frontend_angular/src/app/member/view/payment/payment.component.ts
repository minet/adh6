import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Member, MembershipService, TransactionService } from '../../../api';
import { BuyProductComponent } from './product/buy-product.component';
import { CotisationComponent } from './cotisation/cotisation.component';
import { AbilityModule } from '@casl/angular';
import { MemberDetailService } from '../member-detail.service';

@Component({
  standalone: true,
  imports: [CommonModule, BuyProductComponent, CotisationComponent, AbilityModule],
  selector: 'app-payment',
  templateUrl: './payment.component.html'
})
export class PaymentComponent {
  public member$ = this.memberDetailService.member$;
  public productCollapse: boolean = false;
  public membershipCollapse: boolean = false;
  public paymentMethods$ = this.transactionService.paymentMethodGet();
  public isFree = false;

  constructor(
    private transactionService: TransactionService,
    private membershipService: MembershipService,
    private memberDetailService: MemberDetailService
  ) { }

  public validatePayment(member: Member): void {
    this.membershipService.subscriptionValidate(member.id, this.isFree)
      .subscribe(() => this.memberDetailService.updateMemberInfos.emit("Inscription finie"));
  }

  public subscriptionUpdated() {
    this.memberDetailService.updateMemberInfos.emit("Inscription mise à jour");
    this.membershipCollapse = false;
  }
}
