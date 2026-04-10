import {Component, OnDestroy, OnInit} from "@angular/core";
import {
  ReactiveFormsModule,
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  AbstractControl,
} from "@angular/forms";
import {AccountService, AccountType} from "../../api";
import {takeWhile} from "rxjs/operators";
import {Router} from "@angular/router";
import {Observable} from "rxjs";
import {NotificationService} from "../../notification.service";
import {CommonModule} from "@angular/common";

@Component({
  imports: [CommonModule, ReactiveFormsModule],
  selector: "app-account-create",
  template: `
    <h1 class="title is-1">Création d'un compte</h1>
    <form [formGroup]="accountForm" (ngSubmit)="onSubmit()">
      <div class="field">
        <label>Nom / Intitulé :</label>
        <input
          class="input is-fullwidth"
          type="text"
          formControlName="accountName" />
      </div>
      <div class="field">
        <label for="accountType">Type de compte :</label>
        <select class="input" id="accountType" formControlName="accountType">
          @for (accountType of accountTypes$ | async; track accountType) {
            <option value="{{ accountType.id }}">
              {{ accountType.name }}
            </option>
          }
        </select>
      </div>
      <div class="field">
        <button
          class="button is-primary is-fullwidth"
          type="submit"
          [disabled]="disabled || accountForm.status === 'INVALID'">
          Créer le compte
        </button>
      </div>
    </form>
  `,
})
export class AccountCreateComponent implements OnInit, OnDestroy {
  disabled = false;
  accountForm!: UntypedFormGroup;
  accountTypes$!: Observable<AccountType[]>;

  private alive = true;

  constructor(
    private readonly fb: UntypedFormBuilder,
    private readonly notificationService: NotificationService,
    public accountService: AccountService,
    private readonly router: Router,
  ) {
    this.createForm();
  }

  createForm(): void {
    this.accountForm = this.fb.group({
      accountName: [
        "",
        [(control: AbstractControl) => Validators.required(control)],
      ],
      accountType: [
        1,
        [(control: AbstractControl) => Validators.required(control)],
      ],
    });
  }

  onSubmit(): void {
    this.disabled = true;
    const v = this.accountForm.value as {
      accountName: string;
      accountType: number;
    };

    const account = {
      actif: true,
      name: v.accountName,
      accountType: v.accountType,
    };

    this.accountService
      .accountPost(account)
      .pipe(takeWhile(() => this.alive))
      .subscribe({
        next: () => {
          void this.router.navigate(["/treasury"]);
          this.notificationService.successNotification();
        },
        error: (error) => {
          console.error("Error creating account:", error);
          this.notificationService.errorNotification(
            500,
            "Error",
            "Failed to create account",
          );
          this.disabled = false;
        },
      });
  }

  ngOnInit(): void {
    this.accountTypes$ = this.accountService.accountTypeGet();
  }

  ngOnDestroy(): void {
    this.alive = false;
  }
}
