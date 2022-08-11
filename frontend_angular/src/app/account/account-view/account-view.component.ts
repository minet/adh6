import { Component, OnInit } from '@angular/core';
import { combineLatest, Observable } from 'rxjs';
import { map, share, switchMap } from 'rxjs/operators';
import { AbstractAccount, AccountService, AccountType } from '../../api';
import { ActivatedRoute } from '@angular/router';

import { AppConstantsService } from '../../app-constants.service';
import { Location } from '@angular/common';

@Component({
  selector: 'app-account-view',
  templateUrl: './account-view.component.html',
  styleUrls: ['./account-view.component.scss']
})
export class AccountViewComponent implements OnInit {
  account$: Observable<AbstractAccount>;
  private id$: Observable<number>;
  accountTypes: Array<AccountType>;

  constructor(
    private accountService: AccountService,
    private route: ActivatedRoute,
    private location: Location,
    public appConstantsService: AppConstantsService
  ) { }
  ngOnInit() {
    // id of the account
    this.id$ = this.route.params.pipe(
      map(params => params['account_id'])
    );

    this.appConstantsService.getAccountTypes().subscribe(
      data => {
        this.accountTypes = data;
      }
    );
    // stream, which will emit the account id every time the page needs to be refreshed
    const refresh$ = combineLatest([this.id$])
      .pipe(
        map(([x]) => x),
      );
    this.account$ = refresh$.pipe(
      switchMap(id => this.accountService.accountIdGet(id)),
      share()
    );
  }

  goBack() {
    this.location.back();
  }
}
