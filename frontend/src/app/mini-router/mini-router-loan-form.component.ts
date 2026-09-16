import {
  Component,
  DestroyRef,
  EventEmitter,
  inject,
  Input,
  OnChanges,
  OnInit,
  Output,
} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {HttpErrorResponse} from "@angular/common/http";
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from "@angular/forms";
import {
  catchError,
  debounceTime,
  distinctUntilChanged,
  filter,
  finalize,
  of,
  switchMap,
} from "rxjs";
import {MiniRouterLoan, MiniRouterService, PaymentMethod} from "../api";
import {AppConstantsService} from "../app-constants.service";
import {NotificationService} from "../notification.service";
import {detailOf} from "../shared/http-error";
import {ComboboxComponent, ComboboxOption} from "../ui/combobox.component";
import {MemberSuggestionsService} from "../ui/member-suggestions.service";
import {DEPOSIT_STATUS_LABELS} from "./labels";

const DEFAULT_DEPOSIT = 80;

function isoDate(date: Date): string {
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().slice(0, 10);
}

export function today(): string {
  return isoDate(new Date());
}

function inOneYear(): string {
  const date = new Date();
  date.setFullYear(date.getFullYear() + 1);
  return isoDate(date);
}

// The search combobox holds the typed text until a suggestion is picked
function memberSelected(control: AbstractControl): ValidationErrors | null {
  return typeof control.value === "number" ? null : {memberRequired: true};
}

function returnAfterStart(group: AbstractControl): ValidationErrors | null {
  const {startedAt, returnedAt} = group.value as {
    startedAt?: string;
    returnedAt?: string;
  };
  return startedAt && returnedAt && returnedAt < startedAt
    ? {returnBeforeStart: true}
    : null;
}

/** Creates a loan for a mini-router, or corrects an existing one when given. */
@Component({
  selector: "app-mini-router-loan-form",
  imports: [ReactiveFormsModule, ComboboxComponent],
  templateUrl: "./mini-router-loan-form.component.html",
})
export class MiniRouterLoanFormComponent implements OnInit, OnChanges {
  @Input({required: true}) miniRouterId!: number;
  @Input() loan?: MiniRouterLoan;
  @Output() saved = new EventEmitter<MiniRouterLoan>();

  readonly depositStatuses = Object.entries(DEPOSIT_STATUS_LABELS);
  readonly form = new FormGroup(
    {
      member: new FormControl<string | number | null>(null, memberSelected),
      startedAt: new FormControl(today(), {
        nonNullable: true,
        validators: Validators.required,
      }),
      dueDate: new FormControl(inOneYear(), {nonNullable: true}),
      returnedAt: new FormControl("", {nonNullable: true}),
      depositAmount: new FormControl(DEFAULT_DEPOSIT, {
        nonNullable: true,
        validators: [Validators.required, Validators.min(0)],
      }),
      paymentMethod: new FormControl<number | null>(null),
      depositStatus: new FormControl<MiniRouterLoan.DepositStatusEnum>("held", {
        nonNullable: true,
      }),
    },
    {validators: returnAfterStart},
  );
  paymentMethods: PaymentMethod[] = [];
  memberOptions: ComboboxOption[] = [];
  submitting = false;

  private readonly destroyRef = inject(DestroyRef);
  private readonly miniRouterService = inject(MiniRouterService);
  private readonly memberSuggestions = inject(MemberSuggestionsService);
  private readonly appConstants = inject(AppConstantsService);
  private readonly notificationService = inject(NotificationService);

  get isEdit(): boolean {
    return this.loan?.id != null;
  }

  ngOnInit(): void {
    this.appConstants
      .getPaymentMethods()
      .pipe(
        catchError(() => of([] as PaymentMethod[])),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((methods) => (this.paymentMethods = methods));

    this.form.controls.member.valueChanges
      .pipe(
        filter((value): value is string => typeof value === "string"),
        debounceTime(250),
        distinctUntilChanged(),
        switchMap((terms) =>
          this.memberSuggestions
            .search(terms, undefined, 10, "id")
            .pipe(catchError(() => of([] as ComboboxOption[]))),
        ),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((options) => (this.memberOptions = options));
  }

  ngOnChanges(): void {
    if (!this.loan) return;
    // The member of a loan cannot be changed
    this.form.controls.member.clearValidators();
    this.form.reset({
      member: this.loan.member,
      startedAt: this.loan.startedAt,
      dueDate: this.loan.dueDate ?? "",
      returnedAt: this.loan.returnedAt ?? "",
      depositAmount: this.loan.depositAmount,
      paymentMethod: this.loan.paymentMethod ?? null,
      depositStatus: this.loan.depositStatus ?? "held",
    });
  }

  onSubmit(): void {
    if (this.form.invalid || this.submitting) return;
    const v = this.form.getRawValue();
    const body: MiniRouterLoan = {
      member: v.member as number,
      startedAt: v.startedAt,
      dueDate: v.dueDate || null,
      depositAmount: v.depositAmount,
      paymentMethod: v.paymentMethod,
    };
    const request$ =
      this.loan?.id != null
        ? this.miniRouterService.miniRouterLoanIdPut(this.loan.id, {
            ...body,
            // Clearing the return date of a closed loan is not offered
            returnedAt: this.loan.returnedAt
              ? v.returnedAt || this.loan.returnedAt
              : null,
            depositStatus: v.depositStatus,
          })
        : this.miniRouterService.miniRouterIdLoanPost(this.miniRouterId, body);

    this.submitting = true;
    request$.pipe(finalize(() => (this.submitting = false))).subscribe({
      next: (loan) => {
        this.notificationService.successNotification();
        this.saved.emit(loan);
      },
      error: (error: HttpErrorResponse) => {
        this.notificationService.errorNotification(
          error.status,
          undefined,
          error.status === 409
            ? $localize`:@@mini-router.loan.already-loaned:Ce mini-routeur est déjà prêté.`
            : detailOf(
                error,
                $localize`:@@mini-router.loan.error:Impossible d'enregistrer le prêt.`,
              ),
        );
      },
    });
  }
}
