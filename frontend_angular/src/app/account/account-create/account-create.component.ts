import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AccountService, AccountType } from '../../api';
import { takeWhile } from 'rxjs/operators';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-account-create',
  templateUrl: './account-create.component.html',
  styleUrls: ['./account-create.component.css']
})

export class AccountCreateComponent implements OnInit, OnDestroy {

  disabled = false;
  accountForm: FormGroup;
  accountTypes$: Observable<Array<AccountType>>;

  private alive = true;

  constructor(
    private fb: FormBuilder,
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
