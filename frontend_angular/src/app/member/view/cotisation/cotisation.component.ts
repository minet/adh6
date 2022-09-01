import { Component, Input, Output, EventEmitter } from '@angular/core';
import { finalize, first } from 'rxjs/operators';
import { AbstractAccount, AccountService, AbstractMembership, MembershipService, Account, Member, AbstractMember, SubscriptionBody, PaymentMethod } from '../../../api';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { NotificationService } from '../../../notification.service';

@Component({
  selector: 'app-cotisation',
  templateUrl: './cotisation.component.html',
  styleUrls: ['./cotisation.component.css']
})
export class CotisationComponent {
  @Input() member: Member;
  @Input() paymentMethods: PaymentMethod[];
  @Output() updateSubscription = new EventEmitter<boolean>();

  public amount: number;
  public subscriptionForm: UntypedFormGroup;
  public cotisationDisabled: boolean = false;
  public needSignature: boolean = false;
  public needValidation: boolean = false;
  public isFree: boolean = false;

  // The last one is necessaraly without a room
  private subscriptionPrices: number[] = [0, 9, 18, 27, 36, 45, 50, 9];
  private subscriptionDuration: AbstractMembership.DurationEnum[] = [0, 1, 2, 3, 4, 5, 12, 12];

  private options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };
  private date = new Date;

  constructor(
    private membershipService: MembershipService,
    private accountService: AccountService,
    private fb: UntypedFormBuilder,
    private notificationService: NotificationService,
  ) {
    this.createForm();
  }

  private createForm(): void {
    this.subscriptionForm = this.fb.group({
      renewal: [''],
      paidWith: ['', [Validators.required]]
    });
    this.subscriptionForm.valid
  }

  public submitSubscription() {
    const v = this.subscriptionForm.value;
    let isMembershipFinished = this.member.membership === AbstractMembership.StatusEnum.Aborted || this.member.membership === AbstractMembership.StatusEnum.Cancelled || this.member.membership === AbstractMembership.StatusEnum.Complete;

    // Case where there is no subscription
    this.accountService.accountGet(1, 0, undefined, <AbstractAccount>{
      member: this.member.id
    }, undefined, 'body').pipe(
      first(() => this.cotisationDisabled = true),
      finalize(() => {
        this.cotisationDisabled = false;
      }),
    ).subscribe((response) => {
      if (response.length == 0) {
        this.notificationService.errorNotification(
          404,
          "No Account",
          "There is no account selected for this subscription"
        );
        return;
      }
      const account = response[0];
      const subscription: SubscriptionBody = {
        duration: this.subscriptionDuration.at(v.renewal),
        account: account.id,
        paymentMethod: +v.paidWith,
        member: this.member.id,
        hasRoom: +v.renewal !== this.subscriptionPrices.length - 1
      }
      if (isMembershipFinished) {
        this.membershipService.memberIdSubscriptionPost(this.member.id, subscription, 'body')
          .subscribe(m => {
            if (m.status === AbstractMembership.StatusEnum.PendingRules) {
              this.needSignature = true
            }
            if (m.status === AbstractMembership.StatusEnum.PendingPaymentValidation) {
              this.needSignature = false
            }
            this.notificationService.successNotification(
              "Inscription créée"
            )
            this.updateSubscription.emit(true)
          });
      } else {
        this.membershipService.memberIdSubscriptionPatch(this.member.id, subscription)
          .subscribe(() => {
            this.notificationService.successNotification(
              "Inscription mise à jour"
            )
            this.updateSubscription.emit(true)
          })
      }
    });
  }

  formatDate(monthsToAdd: number): string {
    this.date = new Date();
    if (this.member.departureDate !== undefined) {
      if (this.date.getTime() < new Date(this.member.departureDate).getTime()) {
        this.date = new Date(this.member.departureDate);
      }
    }
    this.date.setMonth(this.date.getMonth() + monthsToAdd);

    return this.date.toLocaleDateString('fr-FR', this.options);
  }

  public updateAmount() {
    this.amount = this.subscriptionPrices.at(this.subscriptionForm.value.renewal);
  }

  get isSubscriptionFinished(): boolean {
    return this.member.membership === "COMPLETE" || this.member.membership === "CANCELLED" || this.member.membership === "ABORTED"
  }
}
