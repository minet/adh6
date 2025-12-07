import {Component, OnDestroy, OnInit} from "@angular/core";
import {
  ReactiveFormsModule,
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  AbstractControl,
} from "@angular/forms";
import {ActivatedRoute, ParamMap, Router} from "@angular/router";

import {AbstractAccount, AccountService, AccountType} from "../../api";
import {Observable} from "rxjs";
import {switchMap, takeWhile} from "rxjs/operators";
import {NotificationService} from "../../notification.service";
import {CommonModule} from "@angular/common";

@Component({
  imports: [CommonModule, ReactiveFormsModule],
  selector: "app-account-edit",
  template: `
    <h1 class="title is-1">Modification d'un compte</h1>
    <form [formGroup]="editAccountForm" (ngSubmit)="onSubmit()" novalidate>
      <div class="field">
        <label>Nom / Intitulé :</label>
        <input
          class="input is-fullwidth"
          type="text"
          formControlName="name"
          [disabled]="true" />
      </div>
      <div class="field">
        <label for="type">Type de compte :</label>
        <select class="input" id="type" formControlName="type">
          @for (accountType of accountTypes$ | async; track accountType) {
            <option value="{{ accountType.id }}">
              {{ accountType.name }}
            </option>
          }
        </select>
      </div>
      <div class="field">
        <input
          type="checkbox"
          class="form-check-input"
          id="accountActive"
          formControlName="actif" />
        <label class="form-check-label" for="accountActive">Actif</label>
      </div>
      <div class="form-group">
        <button
          class="button is-primary is-fullwidth"
          type="submit"
          [disabled]="disabled || editAccountForm.status === 'INVALID'">
          Éditer le compte
        </button>
      </div>
    </form>
  `,
})
export class AccountEditComponent implements OnInit, OnDestroy {
  disabled = false;
  editAccountForm!: UntypedFormGroup;
  accountTypes$!: Observable<AccountType[]>;

  private alive = true;
  private account!: AbstractAccount;

  constructor(
    private readonly accountService: AccountService,
    private readonly route: ActivatedRoute,
    private readonly fb: UntypedFormBuilder,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
  ) {
    this.createForm();
  }

  createForm(): void {
    this.disabled = false;
    this.editAccountForm = this.fb.group({
      name: ["", [(control: AbstractControl) => Validators.required(control)]],
      type: ["", [(control: AbstractControl) => Validators.required(control)]],
      actif: ["", [(control: AbstractControl) => Validators.required(control)]],
    });
  }

  onSubmit(): void {
    this.disabled = true;
    const v = this.editAccountForm.value as {
      name: string;
      actif: boolean;
      type: string;
    };

    const accountPatch: AbstractAccount = {
      name: v.name,
      actif: v.actif,
      accountType: parseInt(v.type, 10),
    };

    this.accountService
      .accountIdPut(this.account.id!, accountPatch, "response")
      .pipe(takeWhile(() => this.alive))
      .subscribe({
        next: () => {
          void this.router.navigate(["/account/view", this.account.id]);
          this.notificationService.successNotification();
        },
        error: (error) => {
          console.error("Error updating account:", error);
          this.notificationService.errorNotification(
            500,
            "Error",
            "Failed to update account",
          );
          this.disabled = false;
        },
      });
  }

  ngOnInit(): void {
    this.accountTypes$ = this.accountService.accountTypeGet();

    this.route.paramMap
      .pipe(
        switchMap((params: ParamMap) => {
          const accountId = params.get("account_id");
          if (!accountId) throw new Error("Account ID not found");
          return this.accountService.accountIdGet(+accountId);
        }),
        takeWhile(() => this.alive),
      )
      .subscribe({
        next: (data: AbstractAccount) => {
          this.account = data;
          this.editAccountForm.patchValue(data);
        },
        error: (error) => {
          console.error("Error fetching account:", error);
          this.notificationService.errorNotification(
            500,
            "Error",
            "Failed to fetch account",
          );
        },
      });
  }

  ngOnDestroy(): void {
    this.alive = false;
  }
}
