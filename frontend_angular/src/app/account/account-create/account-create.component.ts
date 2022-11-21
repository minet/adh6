import { Component, OnDestroy, OnInit } from '@angular/core';
import { ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { AccountService, AccountType } from '../../api';
import { takeWhile } from 'rxjs/operators';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { NotificationService } from '../../notification.service';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  selector: 'app-account-create',
  template: `
  <h1 class="title is-1">Création d'un compte</h1>
  <form [formGroup]="accountForm" (ngSubmit)="onSubmit()">
    <div class="field">
      <label>Nom / Intitulé :</label>
      <input class="input is-fullwidth" type="text" formControlName="accountName" />
    </div>
    <div class="field">
      <label for="accountType">Type de compte :</label>
      <select class="input" id="accountType" formControlName="accountType">
        <option *ngFor="let accountType of accountTypes$ | async" value="{{ accountType.id }}">{{ accountType.name }}</option>
      </select>
    </div>
    <div class="field">
      <button class="button is-primary is-fullwidth" type="submit" [disabled]="disabled || accountForm.status === 'INVALID'">
        Créer le compte
      </button>
    </div>
  </form>
  `
})

export class AccountCreateComponent implements OnInit, OnDestroy {

  disabled = false;
  accountForm: UntypedFormGroup;
  accountTypes$: Observable<Array<AccountType>>;

  private alive = true;

  constructor(
    private fb: UntypedFormBuilder,
    private notificationService: NotificationService,
    public accountService: AccountService,
    private router: Router,
  ) {
    this.createForm();
  }

  createForm() {
    this.accountForm = this.fb.group({
      accountName: ['', [Validators.required]],
      accountType: [1, [Validators.required]],
    });
  }

  onSubmit() {
    this.disabled = true;
    const v = this.accountForm.value;

    const account = {
      actif: true,
      name: v.accountName,
      accountType: parseInt(v.accountType),
    };

    this.accountService.accountPost(account)
      .pipe(takeWhile(() => this.alive))
      .subscribe(res => {
        this.router.navigate(['/treasury']);
        this.notificationService.successNotification();
      });

    this.disabled = false;
  }

  ngOnInit() {
    this.accountTypes$ = this.accountService.accountTypeGet();
  }

  ngOnDestroy() {
    this.alive = false;
  }

}
