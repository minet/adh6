import {Component, OnInit} from '@angular/core';

import {FormBuilder, FormGroup, Validators} from '@angular/forms';

import {first, map, share} from 'rxjs/operators';
import {TreasuryService} from '../api';
import {Observable} from 'rxjs';

@Component({
  selector: 'app-treasury',
  templateUrl: './treasury.component.html',
  styleUrls: ['./treasury.component.css']
})
export class TreasuryComponent implements OnInit {
  cashbox$: Observable<any>;
  balance$: Observable<number>;

  showFundManagement = false;
  fundManagementForm: FormGroup;
  create = false;

  constructor(
    private fb: FormBuilder,
    public treasuryService: TreasuryService,
    ) {
      this.createForm();
  }

  createForm() {
    this.fundManagementForm = this.fb.group({
      toCashRegister: ['', [Validators.min(0)]],
      outOfCashRegister: ['', [Validators.min(0)]],
      toSafe: ['', [Validators.min(0)]],
      outOfSafe: ['', [Validators.min(0)]],
      labelOp: ['', []],
    });
  }

  ngOnInit() {
    this.treasuryService.getCashbox()
      .pipe(
        map((data) => data.fond),
        first(),
      )
      .subscribe((fond) => {

      });

    this.cashbox$ = this.treasuryService.getCashbox().pipe(
      first(),
      share()
    );

    this.balance$ = this.treasuryService.getBank().pipe(
      map(data =>
        data.expectedCav
      ),
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
