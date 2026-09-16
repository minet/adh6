import {Component, inject, Input, OnChanges} from "@angular/core";
import {AsyncPipe, DatePipe} from "@angular/common";
import {RouterModule} from "@angular/router";
import {catchError, map, Observable, of} from "rxjs";
import {MiniRouterLoan, MiniRouterService, PaymentMethod} from "../api";
import {AppConstantsService} from "../app-constants.service";
import {OVERDUE_LABEL} from "./labels";

/** Loans in progress and deposits still held by a member, for the member profile. */
@Component({
  selector: "app-member-mini-routers",
  imports: [AsyncPipe, DatePipe, RouterModule],
  templateUrl: "./member-mini-routers.component.html",
  styles: `
    .loan {
      border: 1px solid var(--app-line);
      border-radius: 0.75rem;
      padding: 1rem 1.25rem;
    }
    .loan + .loan {
      margin-top: 0.75rem;
    }
    .loan.is-overdue {
      border-color: var(--bulma-danger);
    }
    .loan-head {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem 1rem;
      margin-bottom: 0.875rem;
    }
    .loan-title {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }
    .loan-facts {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
      gap: 0.75rem 1.5rem;
      margin: 0;
    }
    .loan-facts dt {
      font-size: 0.75rem;
      color: var(--bulma-text-weak);
    }
    .loan-facts dd {
      margin: 0;
      font-weight: 500;
    }
  `,
})
export class MemberMiniRoutersComponent implements OnChanges {
  @Input({required: true}) memberId!: number;

  readonly overdueLabel = OVERDUE_LABEL;
  loans$: Observable<MiniRouterLoan[]> = of([]);
  paymentMethods: PaymentMethod[] = [];

  private readonly miniRouterService = inject(MiniRouterService);

  constructor() {
    inject(AppConstantsService)
      .getPaymentMethods()
      .pipe(catchError(() => of([] as PaymentMethod[])))
      .subscribe((methods) => (this.paymentMethods = methods));
  }

  ngOnChanges(): void {
    this.loans$ = this.miniRouterService.miniRouterLoanGet(this.memberId).pipe(
      map((loans) =>
        loans.filter(
          (loan) => !loan.returnedAt || loan.depositStatus === "held",
        ),
      ),
      // The section is optional: hide it when the user cannot read loans
      catchError(() => of([] as MiniRouterLoan[])),
    );
  }

  paymentMethodName(id?: number | null): string | undefined {
    return this.paymentMethods.find((method) => method.id === id)?.name;
  }
}
