import {Injectable} from "@angular/core";
import {PaymentMethod, TransactionService} from "./api";
import {Observable, of} from "rxjs";
import {map, share} from "rxjs/operators";

@Injectable({
  providedIn: "root",
})
export class AppConstantsService {
  private paymentMethods?: PaymentMethod[];
  private paymentMethodsObservable?: Observable<PaymentMethod[]> | null;

  constructor(private readonly transactionService: TransactionService) {}

  getPaymentMethods() {
    if (this.paymentMethods) {
      return of(this.paymentMethods);
    } else if (this.paymentMethodsObservable) {
      return this.paymentMethodsObservable;
    } else {
      this.paymentMethodsObservable = this.transactionService
        .paymentMethodGet()
        .pipe(
          map((data) => {
            this.paymentMethodsObservable = null;
            this.paymentMethods = data;
            return this.paymentMethods;
          }),
          share(),
        );
      return this.paymentMethodsObservable;
    }
  }
}
