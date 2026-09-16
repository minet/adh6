import {Component, DestroyRef, inject, OnInit} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {AsyncPipe, DatePipe} from "@angular/common";
import {HttpErrorResponse} from "@angular/common/http";
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {ActivatedRoute, Router, RouterModule} from "@angular/router";
import {AblePipe} from "@casl/angular";
import {
  BehaviorSubject,
  catchError,
  firstValueFrom,
  Observable,
  of,
  switchMap,
} from "rxjs";
import {
  MiniRouter,
  MiniRouterLoan,
  MiniRouterService,
  PaymentMethod,
} from "../api";
import {AppConstantsService} from "../app-constants.service";
import {NotificationService} from "../notification.service";
import {detailOf} from "../shared/http-error";
import {DialogService} from "../ui/dialog.service";
import {ModalComponent} from "../ui/modal.component";
import {
  CONFIG_STATE_LABELS,
  DEPOSIT_STATUS_LABELS,
  depositBadge,
  MODEL_LABELS,
  OVERDUE_LABEL,
} from "./labels";
import {MiniRouterFormComponent} from "./mini-router-form.component";
import {
  MiniRouterLoanFormComponent,
  today,
} from "./mini-router-loan-form.component";

@Component({
  selector: "app-mini-router-details",
  imports: [
    AsyncPipe,
    DatePipe,
    AblePipe,
    RouterModule,
    ReactiveFormsModule,
    ModalComponent,
    MiniRouterFormComponent,
    MiniRouterLoanFormComponent,
  ],
  templateUrl: "./mini-router-details.component.html",
})
export class MiniRouterDetailsComponent implements OnInit {
  readonly modelLabels = MODEL_LABELS;
  readonly configStateLabels = CONFIG_STATE_LABELS;
  readonly depositStatuses = Object.entries(DEPOSIT_STATUS_LABELS);
  readonly depositBadge = depositBadge;
  readonly overdueLabel = OVERDUE_LABEL;

  miniRouterId!: number;
  miniRouter$!: Observable<MiniRouter>;
  loans$!: Observable<MiniRouterLoan[]>;
  paymentMethods: PaymentMethod[] = [];

  editOpen = false;
  loanOpen = false;
  editedLoan: MiniRouterLoan | null = null;
  returnLoan: MiniRouterLoan | null = null;
  submitting = false;
  deleting = false;

  readonly returnForm = new FormGroup({
    returnedAt: new FormControl(today(), {
      nonNullable: true,
      validators: Validators.required,
    }),
    // No default refund: the deposit must be settled deliberately
    depositStatus: new FormControl<MiniRouterLoan.DepositStatusEnum>("held", {
      nonNullable: true,
    }),
  });

  private readonly refresh$ = new BehaviorSubject<void>(undefined);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly miniRouterService = inject(MiniRouterService);
  private readonly appConstants = inject(AppConstantsService);
  private readonly dialogService = inject(DialogService);
  private readonly notificationService = inject(NotificationService);

  ngOnInit(): void {
    this.route.params
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((params) => {
        this.miniRouterId = +params["id"];
        this.miniRouter$ = this.refresh$.pipe(
          switchMap(() =>
            this.miniRouterService.miniRouterIdGet(this.miniRouterId),
          ),
        );
        this.loans$ = this.refresh$.pipe(
          switchMap(() =>
            this.miniRouterService.miniRouterIdLoanGet(this.miniRouterId),
          ),
        );
      });

    this.appConstants
      .getPaymentMethods()
      .pipe(
        catchError(() => of([] as PaymentMethod[])),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((methods) => (this.paymentMethods = methods));
  }

  paymentMethodName(id?: number | null): string {
    return this.paymentMethods.find((method) => method.id === id)?.name ?? "";
  }

  refresh(): void {
    this.refresh$.next();
  }

  onEdited(): void {
    this.editOpen = false;
    this.refresh();
  }

  onLoanSaved(): void {
    this.loanOpen = false;
    this.editedLoan = null;
    this.refresh();
  }

  openReturn(loan: MiniRouterLoan): void {
    this.returnForm.reset();
    this.returnLoan = loan;
  }

  async submitReturn(): Promise<void> {
    const loan = this.returnLoan;
    if (!loan || this.returnForm.invalid || this.submitting) return;
    const v = this.returnForm.getRawValue();
    if (v.returnedAt < loan.startedAt) {
      this.notificationService.errorNotification(
        400,
        undefined,
        $localize`:@@mini-router.loan.dates-error:La date de retour ne peut pas précéder le début du prêt.`,
      );
      return;
    }
    this.submitting = true;
    try {
      const updated = await this.updateLoan(loan, {
        returnedAt: v.returnedAt,
        depositStatus: v.depositStatus,
      });
      if (updated) this.returnLoan = null;
    } finally {
      this.submitting = false;
    }
  }

  async settleDeposit(
    loan: MiniRouterLoan,
    depositStatus: MiniRouterLoan.DepositStatusEnum,
  ): Promise<void> {
    if (this.submitting) return;
    this.submitting = true;
    try {
      await this.updateLoan(loan, {depositStatus});
    } finally {
      this.submitting = false;
    }
  }

  async deleteMiniRouter(miniRouter: MiniRouter): Promise<void> {
    if (miniRouter.id == null || this.deleting) return;
    const confirmed = await this.dialogService.confirm({
      title: $localize`:@@mini-router.delete.title:Supprimer le mini-routeur`,
      text: $localize`:@@mini-router.delete.confirm:Supprimer ${miniRouter.hardwareMac}:hardwareMac: et tout son historique de prêts ? Cette action est irréversible.`,
      confirmText: $localize`:@@common.delete:Supprimer`,
      danger: true,
    });
    if (!confirmed || this.destroyRef.destroyed) return;
    this.deleting = true;
    try {
      await firstValueFrom(
        this.miniRouterService.miniRouterIdDelete(miniRouter.id),
      );
      this.notificationService.successNotification();
      void this.router.navigate(["/mini-router/search"]);
    } catch (error) {
      this.notifyError(
        error,
        $localize`:@@mini-router.delete.blocked:Impossible de supprimer un mini-routeur prêté ou dont une caution n'est pas rendue.`,
        $localize`:@@mini-router.delete.error:Impossible de supprimer le mini-routeur.`,
      );
    } finally {
      this.deleting = false;
    }
  }

  private async updateLoan(
    loan: MiniRouterLoan,
    changes: Partial<MiniRouterLoan>,
  ): Promise<boolean> {
    if (loan.id == null) return false;
    try {
      await firstValueFrom(
        this.miniRouterService.miniRouterLoanIdPut(loan.id, {
          member: loan.member,
          startedAt: loan.startedAt,
          dueDate: loan.dueDate,
          returnedAt: loan.returnedAt,
          depositAmount: loan.depositAmount,
          paymentMethod: loan.paymentMethod,
          depositStatus: loan.depositStatus,
          ...changes,
        }),
      );
      this.notificationService.successNotification();
      this.refresh();
      return true;
    } catch (error) {
      this.notifyError(
        error,
        $localize`:@@mini-router.loan.already-loaned:Ce mini-routeur est déjà prêté.`,
        $localize`:@@mini-router.loan.error:Impossible d'enregistrer le prêt.`,
      );
      return false;
    }
  }

  private notifyError(
    error: unknown,
    conflictMessage: string,
    fallback: string,
  ): void {
    if (this.destroyRef.destroyed) return;
    const status = error instanceof HttpErrorResponse ? error.status : 500;
    this.notificationService.errorNotification(
      status,
      undefined,
      status === 409 ? conflictMessage : detailOf(error, fallback),
    );
  }
}
