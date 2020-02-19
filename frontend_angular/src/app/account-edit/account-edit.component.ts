import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, ParamMap, Router} from '@angular/router';

import {AbstractAccount, Account, AccountService, AccountType} from '../api';
import {NotificationsService} from 'angular2-notifications';
import {Observable} from 'rxjs';
import {switchMap, takeWhile} from 'rxjs/operators';

@Component({
  selector: 'app-account-edit',
  templateUrl: './account-edit.component.html',
  styleUrls: ['./account-edit.component.css']
})

export class AccountEditComponent implements OnInit, OnDestroy {
  disabled = false;
  editAccountForm: FormGroup;
  accountTypes$: Observable<Array<AccountType>>;

  private alive = true;
  private account: Account;

  constructor(
    private accountService: AccountService,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private router: Router,
    private notif: NotificationsService,
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

    console.log(v);

    const accountPatch: AbstractAccount = {
      name: v.name,
      actif: v.actif,
      accountType: parseInt(v.type),
    };

    this.accountService.accountAccountIdPut(accountPatch, this.account.id, 'response')
      .pipe(takeWhile(() => this.alive))
      .subscribe((response) => {
        this.router.navigate(['/account/view', this.account.id]);
        this.notif.success(response.status + ': Success');
      });
    this.disabled = false;
  }


  ngOnInit() {
    this.accountTypes$ = this.accountService.accountTypeGet();

    this.route.paramMap
      .pipe(
        switchMap((params: ParamMap) => this.accountService.accountAccountIdGet(+params.get('account_id'))),
        takeWhile(() => this.alive),
      )
      .subscribe((data: Account) => {
        this.account = data;
        console.log(data);
        this.editAccountForm.patchValue(data);
      });
  }

  ngOnDestroy() {
    this.alive = false;
  }

}
