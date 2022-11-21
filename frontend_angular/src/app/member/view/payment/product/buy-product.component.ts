import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormArray, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { map, Observable } from 'rxjs';
import { Member, PaymentMethod, Product, TreasuryService } from '../../../../api';
import { Toast } from '../../../../notification.service';

interface ProductForm {
  paidWith: FormControl<number>;
  products: FormArray<FormGroup<{
    id: FormControl<number>;
    name: FormControl<string>;
    checked: FormControl<boolean>;
    amount: FormControl<number>;
  }>>;
}

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  selector: 'app-buy-product',
  templateUrl: './buy-product.component.html'
})
export class BuyProductComponent {
  @Input() member: Member;
  @Input() paymentMethods: PaymentMethod[];

  public productForm: FormGroup<ProductForm> = new FormGroup({
    paidWith: new FormControl(0, {nonNullable: true, validators: [Validators.required, Validators.min(1)]}),
    products: new FormArray([])
  });
  public products$: Observable<Product[]>;

  constructor(private treasuryService: TreasuryService) {
    this.products$ = this.treasuryService.productGet(100, 0, undefined, "body")
      .pipe(
        map(products => {
          products.forEach((product) => {
            this.productForm.controls.products.push(new FormGroup({
              id: new FormControl(product.id),
              checked: new FormControl<boolean>(false),
              name: new FormControl(product.name),
              amount: new FormControl(product.sellingPrice)
            }))
          })
          return products;
        })
      );
  }

  private get checkedProducts() {
    return this.productForm.value.products.filter(p => p.checked === true)
  }

  public get amount(): number {
    let v = 0;
    this.checkedProducts.forEach(p => v += p.amount)
    return v
  }

  public submit(): void {
    if (this.checkedProducts.length === 0) return
    this.treasuryService.productBuyPost(this.member.id, this.checkedProducts.map(p => p.id), this.productForm.value.paidWith)
      .subscribe(() => {
        Toast.fire({
          title: "Produit(s) acheté(s)",
          icon: 'success'
        })
        this.productForm.controls.products.controls.forEach(e => e.controls.checked.patchValue(false));
        this.productForm.controls.paidWith.patchValue(0)
      }
    );
  }
}
