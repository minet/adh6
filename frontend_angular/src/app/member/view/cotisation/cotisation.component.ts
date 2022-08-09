import { Component, Input } from '@angular/core';
import { finalize, first } from 'rxjs/operators';
import { AbstractAccount, AccountService, AbstractMembership, MembershipService, Account, Member, AbstractMember, SubscriptionBody, PaymentMethod } from '../../../api';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NotificationService } from '../../../notification.service';

@Component({
  selector: 'app-cotisation',
  templateUrl: './cotisation.component.html',
  styleUrls: ['./cotisation.component.css']
})
export class CotisationComponent {
  @Input() member: Member;
  @Input() paymentMethods: PaymentMethod[];
  public amount: number;

  public subscriptionForm: FormGroup;
  public cotisationDisabled: boolean = false;
  public needSignature: boolean = false;
  public needValidation: boolean = false;
  public isFree: boolean = false;

  private subscriptionPrices: number[] = [0, 9, 18, 27, 36, 45, 50, 9];
  private subscriptionDuration: AbstractMembership.DurationEnum[] = [0, 1, 2, 3, 4, 5, 12, 12];
  private options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };
  private date = new Date;

  constructor(
    private membershipService: MembershipService,
    private accountService: AccountService,
    private fb: FormBuilder,
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

  /*updateForm(): void {
    
    if (this.membership == undefined || this.membership.duration == undefined) return
    let paymentMethod: number = 0;
    if (this.membership.paymentMethod == undefined) {
      paymentMethod = 0;
    } else if (typeof (this.membership.paymentMethod) === 'number') {
      paymentMethod = this.membership.paymentMethod;
    } else {
      paymentMethod = this.membership.paymentMethod;
    }
    
    this.subscriptionForm.patchValue({
      renewal: '', // (this.membership.duration) ? this.subscriptionDuration.indexOf(this.membership.duration) : '',
      paidWith: '' // (paymentMethod != 0) ? paymentMethod : ''
    });
  }
  */

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
        member: this.member.id
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
          });
      } else {
        this.membershipService.memberIdSubscriptionPatch(this.member.id, subscription)
          .subscribe(() => this.notificationService.successNotification(
            "Inscription mise à jour"
          ))
      }
    });
  }

  public validatePayment(): void {
    this.membershipService.subscriptionValidate(this.member.id, (this.isFree) ? this.isFree : undefined).subscribe(() => {
      this.notificationService.successNotification(
        "Inscription finie",
        "L'inscription pour cet adhérent est finie"
      );
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
}
