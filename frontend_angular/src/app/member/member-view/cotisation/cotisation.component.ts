import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import {Observable} from 'rxjs';
import {finalize, first, map} from 'rxjs/operators';
import {AbstractAccount, AccountService, DeviceService, MemberService, Membership, Product, TransactionService, TreasuryService, PaymentMethod, AbstractMembership, MembershipService, Account, Member} from '../../../api';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppConstantsService } from '../../../app-constants.service';
import { NotificationService } from '../../../notification.service';

@Component({
  selector: 'app-cotisation',
  templateUrl: './cotisation.component.html',
  styleUrls: ['./cotisation.component.css']
})
export class CotisationComponent implements OnInit {
  @Input() member: Member;
  @Input() memberId: number;
  @Input() membership: Membership;

  @Output() membershipUpdated: EventEmitter<number> = new EventEmitter<number>();

  public subscriptionForm: FormGroup;
  public products$: Observable<Product[]>;
  public paymentMethods$: Observable<PaymentMethod[]>;
  public amountToPay: number = 0;
  public cotisationDisabled: boolean = false;

  private subscriptionPrices: number[] = [0, 9, 18, 27, 36, 45, 50, 9];
  private subscriptionDuration: AbstractMembership.DurationEnum[] = [0, 1, 2, 3, 4, 5, 12, 12];
  private options: Intl.DateTimeFormatOptions = {year: 'numeric', month: 'long', day: 'numeric'};
  private date = new Date;

  constructor(
    public memberService: MemberService,
    public membershipService: MembershipService,
    public deviceService: DeviceService,
    public transactionService: TransactionService,
    public accountService: AccountService,
    private treasuryService: TreasuryService,
    private fb: FormBuilder,
    private notificationService: NotificationService,
  ) { 
    this.createForm();
  }

  ngOnInit() {
    this.paymentMethods$ = this.transactionService.paymentMethodGet();
    const canBeUpdated = this.membership.status != AbstractMembership.StatusEnum.ABORTED && this.membership.status != AbstractMembership.StatusEnum.CANCELLED && this.membership.status != AbstractMembership.StatusEnum.COMPLETE;
    this.setupProducts(canBeUpdated);
    if (canBeUpdated) this.updateForm();
  }

  createForm(): void {
    this.subscriptionForm = this.fb.group({
      renewal: ['0', [Validators.required]],
      products: this.fb.array([]),
      paidWith: ['0', [Validators.required]],
    });
  }

  updateForm(): void {
    console.log(this.membership);
    if (this.membership == undefined || this.membership.duration == undefined) return
    let paymentMethod: number = 0;
    if (this.membership.paymentMethod == undefined) {
      paymentMethod = 0;
    } else if (typeof(this.membership.paymentMethod) === 'number') {
      paymentMethod = this.membership.paymentMethod;
    } else {
      paymentMethod = this.membership.paymentMethod.id;
    }
    console.log({
      renewal: this.subscriptionDuration.indexOf(AbstractMembership.DurationEnum.NUMBER_2),
      paidWith: paymentMethod
    });
    this.subscriptionForm.patchValue({
      renewal: this.subscriptionDuration.indexOf(this.membership.duration),
      paidWith: paymentMethod
    });
    this.updateAmount();
  }

  setupProducts(canBeUpdated: boolean): void {
    this.products$ = this.treasuryService.productGet(100, 0, undefined, "body")
      .pipe(
        map(products => {
          products.forEach((product) => {
            this.productsFormArray.push(this.fb.group({
              id: [{value: product.id}],
              checked: [this.membership.products.indexOf(product.id) != -1 && canBeUpdated, [Validators.required]],
              amount: [{value: product.sellingPrice}]
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

  submitSubscription() {
    const v = this.subscriptionForm.value;
    console.log(v);
    let products = [];
    for (let i = 0; i < this.productsFormArray.length; i++) {
      if (this.productsFormArray.at(i).value.checked === true) {
        products.push(+this.productsFormArray.at(i).value.id.value)
      }
    }
    this.accountService.accountGet(1, 0, undefined, <AbstractAccount>{
      member: this.memberId
    }, 'response').pipe(
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
      console.log(account);
      this.paymentMethods$.subscribe((paymentMethods) => {
        let paymentMethod: PaymentMethod;
        paymentMethods.forEach((elem) => {
          if (elem.id == +v.paidWith) { paymentMethod = elem }
        })
        console.log(paymentMethod);
        const subscription: AbstractMembership = {
          duration: this.subscriptionDuration[v.renewal],
          account: account.id,
          products: products,
          paymentMethod: paymentMethod.id,
          hasRoom: +v.renewal !== 7
        }
        this.membershipService.memberMemberIdMembershipUuidPatch(subscription, this.memberId, this.membership.uuid).subscribe(() => {
          this.membershipUpdated.emit(this.memberId);
          this.notificationService.successNotification(
            "Membership updated",
            "The membership for this member has been updated"
          );
        })
      });
    });
  }

  updateAmount() {
    this.amountToPay = 0;
    this.amountToPay = this.amountToPay + this.subscriptionPrices[this.subscriptionForm.value.renewal];

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
