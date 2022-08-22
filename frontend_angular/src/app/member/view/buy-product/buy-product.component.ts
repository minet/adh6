import { Component, Input, OnInit } from '@angular/core';
import { UntypedFormArray, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { finalize, map, Observable, shareReplay } from 'rxjs';
import { Member, PaymentMethod, Product, TreasuryService } from '../../../api';
import { NotificationService } from '../../../notification.service';

@Component({
  selector: 'app-buy-product',
  templateUrl: './buy-product.component.html',
  styleUrls: ['./buy-product.component.sass']
})
export class BuyProductComponent implements OnInit {
  @Input() member: Member;
  @Input() paymentMethods: PaymentMethod[];

  public productsForm: UntypedFormGroup;
  public products$: Observable<Product[]>;
  public amountToPay: number = 0;

  constructor(
    private treasuryService: TreasuryService,
    private fb: UntypedFormBuilder,
    private notificationService: NotificationService,
  ) { }

  ngOnInit(): void {
    this.createForm()
    this.resetProducts()
  }

  get productsFormArray(): UntypedFormArray {
    return this.productsForm.get('products') as UntypedFormArray
  }

  private createForm(): void {
    this.productsForm = this.fb.group({
      products: this.fb.array([]),
      paidWith: ['', [Validators.required]]
    });
  }

  private resetProducts(): void {
    this.products$ = this.treasuryService.productGet(100, 0, undefined, "body")
      .pipe(
        shareReplay(1),
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

  public submit(): void {
    const v = this.productsForm.value;
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

  public updateAmount() {
    this.amountToPay = 0;
    for (let i = 0; i < this.productsFormArray.length; i++) {
      if (this.productsFormArray.at(i).value.checked === true) {
        this.amountToPay += +this.productsFormArray.at(i).value.amount.value;
      }
    }
  }
}
