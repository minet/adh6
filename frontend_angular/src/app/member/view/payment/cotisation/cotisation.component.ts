import { Component, Input, Output, EventEmitter } from '@angular/core';
import { AbstractAccount, AccountService, Membership, MembershipService, Member, PaymentMethod, SubscriptionBody } from '../../../../api';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Toast } from '../../../../notification.service';
import { CommonModule } from '@angular/common';

interface SubscriptionForm {
  paidWith: FormControl<number>;
  durationIndex: FormControl<number>;
}

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  selector: 'app-cotisation',
  templateUrl: './cotisation.component.html'
})
export class CotisationComponent {
  @Input() member: Member;
  @Input() paymentMethods: PaymentMethod[];
  @Output() updateSubscription = new EventEmitter<boolean>();

  public subscriptionForm: FormGroup<SubscriptionForm> = new FormGroup({
    paidWith: new FormControl(-1, [Validators.min(1
      )]),
    durationIndex: new FormControl(-1, [Validators.min(0)])
  });
  public needSignature: boolean = false;
  public needValidation: boolean = false;

  // The last one is necessaraly without a room
  public subscriptionPrices: number[] = [9, 18, 27, 36, 45, 50, 9];
  public subscriptionDuration: Membership.DurationEnum[] = [1, 2, 3, 4, 5, 12, 12];

  private options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };

  constructor(
    private membershipService: MembershipService,
    private accountService: AccountService,
  ) {}

  public get amount(): number {
    return this.subscriptionForm.value.durationIndex !== -1 ? this.subscriptionPrices.at(this.subscriptionForm.value.durationIndex) : 0;
  }

  public submitSubscription() {
    const v = this.subscriptionForm.value;
    // Case where there is no subscription
    this.accountService.accountGet(1, 0, undefined, <AbstractAccount>{
      member: this.member.id
    }).subscribe((response) => {
      if (response.length == 0) {
        Toast.fire("No Account found")
        return;
      }
      console.log(response[0]);
      const subscription: SubscriptionBody = {
        duration: this.subscriptionDuration.at(+v.durationIndex),
        account: response[0].id,
        paymentMethod: +v.paidWith,
        member: this.member.id,
        hasRoom: +v.durationIndex !== this.subscriptionPrices.length - 1
      }
      if (this.isSubscriptionFinished) {
        this.membershipService.memberIdSubscriptionPost(this.member.id, subscription, 'body')
          .subscribe(m => {
            if (m.status === Membership.StatusEnum.PendingRules) {
              this.needSignature = true
            }
            if (m.status === Membership.StatusEnum.PendingPaymentValidation) {
              this.needSignature = false
            }
            Toast.fire("Inscription créée")
            this.updateSubscription.emit(true)
          });
      } else {
        this.membershipService.memberIdSubscriptionPatch(this.member.id, subscription)
          .subscribe(() => {
            Toast.fire("Inscription mise à jour")
            this.updateSubscription.emit(true)
          })
      }
    });
  }

  formatDate(monthsToAdd: number): string {
    let date = (new Date().getTime() < new Date(this.member.departureDate).getTime()) ? new Date(this.member.departureDate) : new Date();
    date.setMonth(date.getMonth() + monthsToAdd);
    return date.toLocaleDateString('fr-FR', this.options);
  }

  get isSubscriptionFinished(): boolean {
    return this.member.membership === Membership.StatusEnum.Complete || this.member.membership === Membership.StatusEnum.Cancelled || this.member.membership === Membership.StatusEnum.Aborted
  }
}
