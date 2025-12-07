import {CommonModule} from "@angular/common";
import {Component, Input} from "@angular/core";
import {
  FormArray,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {map, Observable} from "rxjs";
import {
  AbstractMember,
  PaymentMethod,
  Product,
  TreasuryService,
} from "../../../../api";
import {Toast} from "../../../../notification.service";

interface ProductForm {
  paidWith: FormControl<number>;
  products: FormArray<
    FormGroup<{
      id: FormControl<number>;
      name: FormControl<string>;
      checked: FormControl<boolean>;
      amount: FormControl<number>;
    }>
  >;
}

@Component({
  imports: [CommonModule, ReactiveFormsModule],
  selector: "app-buy-product",
  templateUrl: "./buy-product.component.html",
})
export class BuyProductComponent {
  @Input() member!: AbstractMember;
  @Input() paymentMethods!: PaymentMethod[];

  public productForm: FormGroup<ProductForm> = new FormGroup({
    paidWith: new FormControl(0, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1)],
    }),
    products: new FormArray<
      FormGroup<{
        id: FormControl<number>;
        name: FormControl<string>;
        checked: FormControl<boolean>;
        amount: FormControl<number>;
      }>
    >([]),
  });
  public products$: Observable<Product[]>;

  constructor(private readonly treasuryService: TreasuryService) {
    this.products$ = this.treasuryService
      .productGet(100, 0, undefined, "body")
      .pipe(
        map((products) => {
          products.forEach((product) => {
            this.productForm.controls.products.push(
              new FormGroup({
                id: new FormControl(product.id!, {nonNullable: true}),
                checked: new FormControl<boolean>(false, {nonNullable: true}),
                name: new FormControl(product.name, {nonNullable: true}),
                amount: new FormControl(product.sellingPrice, {
                  nonNullable: true,
                }),
              }),
            );
          });
          return products;
        }),
      );
  }

  private get checkedProducts() {
    const products = this.productForm.value.products;
    return products ? products.filter((p) => p.checked === true) : [];
  }

  public get amount(): number {
    let v = 0;
    this.checkedProducts.forEach((p) => {
      if (p.amount != null) {
        v += p.amount;
      }
    });
    return v;
  }

  updateAmount(): void {
    // Method called when checkboxes change - the amount getter will recalculate automatically
  }

  public submit(): void {
    if (this.checkedProducts.length === 0) {
      return;
    }

    if (this.member.id == null) {
      void Toast.fire({
        title: "Erreur",
        text: "Membre non valide",
        icon: "error",
      });
      return;
    }

    const productIds = this.checkedProducts
      .map((p) => p.id)
      .filter((id): id is number => id != null);

    const paymentMethod = this.productForm.value.paidWith;
    if (paymentMethod == null) {
      void Toast.fire({
        title: "Erreur",
        text: "Méthode de paiement requise",
        icon: "error",
      });
      return;
    }

    this.treasuryService
      .productBuyPost(this.member.id, productIds, paymentMethod)
      .subscribe(() => {
        void Toast.fire({
          title: "Produit(s) acheté(s)",
          icon: "success",
        });
        this.productForm.controls.products.controls.forEach((e) =>
          e.controls.checked.patchValue(false),
        );
        this.productForm.controls.paidWith.patchValue(0);
      });
  }
}
