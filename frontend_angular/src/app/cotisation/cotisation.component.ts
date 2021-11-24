import { Component, Input, OnInit } from '@angular/core';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import {AbstractAccount, AccountService, DeviceService, MemberService, Membership, Product, TransactionService, TreasuryService, PaymentMethod, AbstractMembership, MembershipService} from '../api';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-cotisation',
  templateUrl: './cotisation.component.html',
  styleUrls: ['./cotisation.component.css']
})
export class CotisationComponent implements OnInit {
  @Input() memberId: number;
  @Input() membership: Membership;

  public subscriptionForm: FormGroup;
  public products$: Observable<Product[]>;
  public paymentMethods$: Observable<PaymentMethod[]>;
  public amountToPay: number = 0;
  public cotisation: boolean = true;

  private subscriptionPrices: number[] = [0, 9, 18, 27, 36, 45, 50, 9];
  private subscriptionDuration: AbstractMembership.DurationEnum[] = [0, 1, 2, 3, 4, 5, 12, 12];
  private options: Intl.DateTimeFormatOptions = {year: 'numeric', month: 'long', day: 'numeric'};
  private date = new Date;

  constructor(
    public memberService: MemberService,
    public deviceService: DeviceService,
    public transactionService: TransactionService,
    public accountService: AccountService,
    private treasuryService: TreasuryService,
    private fb: FormBuilder,
  ) { 
    this.createForm();
  }

  ngOnInit() {
    this.paymentMethods$ = this.transactionService.paymentMethodGet();
    this.setupProducts();
    this.updateForm();
  }

  createForm(): void {
    this.subscriptionForm = this.fb.group({
      renewal: ['0', [Validators.required]],
      products: this.fb.array([]),
      paidWith: ['0', [Validators.required]],
    });
  }

  updateForm(): void {
    if (this.membership == undefined || this.membership.paymentMethod == undefined || this.membership.duration == undefined) {
      return
    }
    let paymentMethod: number = 0;
    if (this.membership.paymentMethod == undefined) {
      paymentMethod = 0;
    } else if (typeof(this.membership.paymentMethod) === 'number') {
      paymentMethod = this.membership.paymentMethod;
    } else {
      paymentMethod = this.membership.paymentMethod.id;
    }
    this.subscriptionForm.patchValue({
      renewal: this.subscriptionDuration.indexOf(AbstractMembership.DurationEnum.NUMBER_2),
      paidWith: paymentMethod
    });
  }

  setupProducts(): void {
    this.products$ = this.treasuryService.productGet(100, 0, undefined, "body")
      .pipe(
        map(products => {
          products.forEach((product) => {
            this.productsFormArray.push(this.fb.group({
              id: [{value: product.id}],
              checked: [false, [Validators.required]],
              amount: [{value: product.sellingPrice}]
            }))
          })
          return products;
        })
      );
  }

  get productsFormArray(): FormArray {
    return this.subscriptionForm.get('products') as FormArray
  }

  submitSubscription() {
    const v = this.subscriptionForm.value;
    let products = [];
    for (let i = 0; i < this.productsFormArray.length; i++) {
      if (this.productsFormArray.at(i).value.checked === true) {
        products.push(+this.productsFormArray.at(i).value.id.value)
      }
    }

    const abstractAccount: AbstractAccount = {
      member: this.memberId
    };
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
    this.date.setMonth(this.date.getMonth() + monthsToAdd);

    return this.date.toLocaleDateString('fr-FR', this.options);
  }
}
