import { Component, OnInit } from '@angular/core';

import { ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';

import { first, map, share } from 'rxjs/operators';
import { TreasuryService } from '../api';
import { Observable } from 'rxjs';
import { CommonModule } from '@angular/common';
import { AccountListComponent } from '../account/account-list/account-list.component';

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, AccountListComponent],
  selector: 'app-treasury',
  templateUrl: './treasury.component.html'
})
export class TreasuryComponent implements OnInit {
  cashbox$: Observable<any> = new Observable();
  balance$: Observable<any> = new Observable();

  showFundManagement = false;
  fundManagementForm: UntypedFormGroup;
  create = false;

  constructor(
    private fb: UntypedFormBuilder,
    public treasuryService: TreasuryService,
  ) {
    this.fundManagementForm = this.fb.group({
      toCashRegister: ['', [Validators.min(0)]],
      outOfCashRegister: ['', [Validators.min(0)]],
      toSafe: ['', [Validators.min(0)]],
      outOfSafe: ['', [Validators.min(0)]],
      labelOp: ['', []],
    });
  }

  ngOnInit() {
    this.treasuryService.getCashbox().pipe(map((data) => data.fond)).subscribe();
    this.cashbox$ = this.treasuryService.getCashbox();

    this.balance$ = this.treasuryService.getBank().pipe(
      map(data =>
        data.expectedCav),
      first(),
      share()
    );
  }

  onSubmit() {
    // TODO
    console.log('onSubmit() à compléter');
  }

  toggleFundManagement() {
    this.showFundManagement = !this.showFundManagement;
  }
}
