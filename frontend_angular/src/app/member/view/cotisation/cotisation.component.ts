import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { Observable } from 'rxjs';
import { finalize, first, map } from 'rxjs/operators';
import { AbstractAccount, AccountService, Membership, Product, TransactionService, TreasuryService, PaymentMethod, AbstractMembership, MembershipService, Account, Member } from '../../../api';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NotificationService } from '../../../notification.service';

@Component({
  selector: 'app-cotisation',
  templateUrl: './cotisation.component.html',
  styleUrls: ['./cotisation.component.css']
})
export class CotisationComponent implements OnInit {
  @Input() member: Member;
  @Input() membership: Membership;

  @Output() memberPaymentUpdated: EventEmitter<number> = new EventEmitter<number>();

  public subscriptionForm: FormGroup;
  public products$: Observable<Product[]>;
  public paymentMethods$: Observable<PaymentMethod[]>;
  public amountToPay: number = 0;
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
    private transactionService: TransactionService,
    private accountService: AccountService,
    private treasuryService: TreasuryService,
    private fb: FormBuilder,
    private notificationService: NotificationService,
  ) {
    this.createForm();
  }

  ngOnInit() {
    this.paymentMethods$ = this.transactionService.paymentMethodGet();
    const canBeUpdated = this.membership.status != AbstractMembership.StatusEnum.ABORTED && this.membership.status != AbstractMembership.StatusEnum.CANCELLED && this.membership.status != AbstractMembership.StatusEnum.COMPLETE;
    this.resetProducts();
    if (canBeUpdated) this.updateForm();
  }

  private createForm(): void {
    this.subscriptionForm = this.fb.group({
      renewal: [''],
      products: this.fb.array([]),
      paidWith: ['', [Validators.required]]
    });
    this.subscriptionForm.valid
  }

  updateForm(): void {
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
      renewal: (this.membership.duration) ? this.subscriptionDuration.indexOf(this.membership.duration) : '',
      paidWith: (paymentMethod != 0) ? paymentMethod : ''
    });
  }

  private resetProducts(): void {
    this.products$ = this.treasuryService.productGet(100, 0, undefined, "body")
      .pipe(
        map(products => {
          this.productsFormArray.clear();
          products.forEach((product) => {
            this.productsFormArray.push(this.fb.group({
              id: [{ value: product.id }],
              checked: [''],
              amount: [{ value: product.sellingPrice }]
            }))
          })
          return products;
        }),
        finalize(() => this.updateAmount())
      );
  }

  get productsFormArray(): FormArray {
    return this.subscriptionForm.get('products') as FormArray
  }

  public submitSubscription() {
    const v = this.subscriptionForm.value;
    let isMembershipFinished = this.membership.status === AbstractMembership.StatusEnum.ABORTED || this.membership.status === AbstractMembership.StatusEnum.CANCELLED || this.membership.status === AbstractMembership.StatusEnum.COMPLETE;
    if (!v.renewal && isMembershipFinished) {
      this.buyProducts();
      return;
    }

    // Case where there is no subscription
    this.accountService.accountGet(1, 0, undefined, <AbstractAccount>{
      member: this.member.id
    }, undefined, 'response').pipe(
      first(() => this.cotisationDisabled = true),
      finalize(() => {
        this.cotisationDisabled = false;
      }),
    ).subscribe((response) => {
      if (+response.headers.get('x-total-count') == 0) {
        this.notificationService.errorNotification(
          404,
          "No Account",
          "There is no account selected for this subscription"
        );
        return;
      }
      const account: Account = response.body[0];
      this.paymentMethods$.subscribe((paymentMethods) => {
        let paymentMethod: PaymentMethod;
        paymentMethods.forEach((elem) => {
          if (elem.id == +v.paidWith) { paymentMethod = elem }
        })
        if (isMembershipFinished) {
          const subscription: Membership = {
            duration: this.subscriptionDuration.at(v.renewal),
            account: account.id,
            products: [],
            paymentMethod: paymentMethod.id,
            hasRoom: +v.renewal !== 7,
            status: AbstractMembership.StatusEnum.INITIAL,
            member: this.member.id
          }
          this.membershipService.memberIdMembershipPost(subscription, this.member.id, 'body')
            .subscribe(m => {
              if (m.status === AbstractMembership.StatusEnum.PENDINGRULES) {
                this.needSignature = true
              }
              if (m.status === AbstractMembership.StatusEnum.PENDINGPAYMENTVALIDATION) {
                this.needSignature = true
              }
              this.membership = m;
            });
        } else {
          const subscription: AbstractMembership = {
            duration: this.subscriptionDuration.at(v.renewal),
            account: account.id,
            products: [],
            paymentMethod: paymentMethod.id,
            hasRoom: +v.renewal !== 7,
            member: this.member.id
          }
          this.membershipService.memberIdMembershipUuidPatch(subscription, this.member.id, this.membership.uuid)
            .subscribe(() => this.notificationService.successNotification(
              "Inscription mise à jour"
            ))
        }
      });
    });
  }

  private buyProducts(): void {
    const v = this.subscriptionForm.value;
    let products = [];
    for (let i = 0; i < this.productsFormArray.length; i++) {
      if (this.productsFormArray.at(i).value.checked === true) {
        products.push(+this.productsFormArray.at(i).value.id.value)
      }
    }
    if (products.length === 0) {
      return;
    }

    this.treasuryService.productBuyPost(this.member.id, products, +v.paidWith).subscribe(
      () => {
        this.notificationService.successNotification("Produits achetés");
        this.resetProducts();
      }
    );
  }

  public validatePayment(): void {
    this.membershipService.membershipValidate(this.member.id, this.membership.uuid, (this.isFree) ? this.isFree : undefined).subscribe(() => {
      this.notificationService.successNotification(
        "Inscription finie",
        "L'inscription pour cet adhérent est finie"
      );
      this.memberPaymentUpdated.emit(this.member.id);
      this.buyProducts();
    });
  }

  public updateAmount() {
    this.amountToPay = 0;
    this.amountToPay = this.amountToPay + this.subscriptionPrices.at(this.subscriptionForm.value.renewal);

    for (let i = 0; i < this.productsFormArray.length; i++) {
      if (this.productsFormArray.at(i).value.checked === true) {
        this.amountToPay += +this.productsFormArray.at(i).value.amount.value;
      }
    }
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
}
