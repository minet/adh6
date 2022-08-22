import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { AbstractAccount, Account, AccountService, AccountType } from '../../api';
import { Observable } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-account-edit',
  templateUrl: './account-edit.component.html',
  styleUrls: ['./account-edit.component.css']
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
