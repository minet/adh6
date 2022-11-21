import { Component, OnDestroy, OnInit } from '@angular/core';
import { ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { AbstractAccount, Account, AccountService, AccountType } from '../../api';
import { Observable } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  selector: 'app-account-edit',
  template: `
  <h1 class="title is-1">Modification d'un compte</h1>
  <form [formGroup]="editAccountForm" (ngSubmit)="onSubmit()" novalidate>
    <div class="field">
      <label>Nom / Intitulé :</label>
      <input class="input is-fullwidth" type="text" formControlName="name" disabled />
    </div>
    <div class="field">
      <label for="type">Type de compte :</label>
      <select class="input" id="type" formControlName="type">
        <option *ngFor="let accountType of accountTypes$ | async" value="{{ accountType.id }}">{{ accountType.name }}</option>
      </select>
    </div>
    <div class="field">
      <input type="checkbox" class="form-check-input" id="accountActive" formControlName="actif">
      <label class="form-check-label" for="accountActive">Actif</label>
    </div>
    <div class="form-group">
      <button class="button is-primary is-fullwidth" type="submit" [disabled]="disabled || editAccountForm.status === 'INVALID'">
        Éditer le compte
      </button>
    </div>
  </form>
  `
})

export class AccountEditComponent implements OnInit, OnDestroy {
  disabled = false;
  editAccountForm: UntypedFormGroup;
  accountTypes$: Observable<Array<AccountType>>;

  private alive = true;
  private account: Account;

  constructor(
    private accountService: AccountService,
    private route: ActivatedRoute,
    private fb: UntypedFormBuilder,
    private router: Router,
    private notificationService: NotificationService,
  ) {
    this.createForm();
  }

  createForm() {
    this.disabled = false;
    this.editAccountForm = this.fb.group({
      name: ['', [Validators.required]],
      type: ['', [Validators.required]],
      actif: ['', [Validators.required]]
    });
  }

  onSubmit() {
    this.disabled = true;
    const v = this.editAccountForm.value;

    const accountPatch: AbstractAccount = {
      name: v.name,
      actif: v.actif,
      accountType: parseInt(v.type),
    };

    this.accountService.accountIdPut(this.account.id, accountPatch, 'response')
      .pipe(takeWhile(() => this.alive))
      .subscribe(() => {
        this.router.navigate(['/account/view', this.account.id]);
        this.notificationService.successNotification();
      });
    this.disabled = false;
  }


  ngOnInit() {
    this.accountTypes$ = this.accountService.accountTypeGet();

    this.route.paramMap
      .pipe(
        switchMap((params: ParamMap) => this.accountService.accountIdGet(+params.get('account_id'))),
        takeWhile(() => this.alive),
      )
      .subscribe((data: Account) => {
        this.account = data;
        this.editAccountForm.patchValue(data);
      });
  }

  ngOnDestroy() {
    this.alive = false;
  }

}
