import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {Component} from "@angular/core";
import {
  AbstractMember,
  MembershipService,
  TransactionService,
} from "../../../api";
import {BuyProductComponent} from "./product/buy-product.component";
import {CotisationComponent} from "./cotisation/cotisation.component";
import {AblePipe} from "@casl/angular";
import {MemberDetailService} from "../member-detail.service";

@Component({
  standalone: true,
  imports: [
    CommonModule,
    BuyProductComponent,
    CotisationComponent,
    AblePipe,
    FormsModule,
  ],
  selector: "app-payment",
  templateUrl: "./payment.component.html",
})
export class PaymentComponent {
  public member$ = this.memberDetailService.member$;
  public productCollapse = false;
  public membershipCollapse = false;
  public paymentMethods$ = this.transactionService.paymentMethodGet();
  public isFree = false;

  constructor(
    private readonly transactionService: TransactionService,
    private readonly membershipService: MembershipService,
    private readonly memberDetailService: MemberDetailService,
  ) {}

  public validatePayment(member: AbstractMember): void {
    this.membershipService
      .subscriptionValidate(member.id!, this.isFree)
      .subscribe(() =>
        this.memberDetailService.updateMemberInfos.emit("Inscription finie"),
      );
  }

  public subscriptionUpdated() {
    this.memberDetailService.updateMemberInfos.emit("Inscription mise à jour");
    this.membershipCollapse = false;
  }
}
