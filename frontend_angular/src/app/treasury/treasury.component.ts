import {Component, OnInit} from '@angular/core';

import {FormBuilder, FormGroup, Validators} from '@angular/forms';

import {TreasuryService} from '../api';

import {first, map} from 'rxjs/operators';

@Component({
  selector: 'app-treasury',
  templateUrl: './treasury.component.html',
  styleUrls: ['./treasury.component.css']
})
export class TreasuryComponent implements OnInit {
  fond = 0;
  balance = 0;

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
    this.treasuryService.getCaisse()
      .pipe(
        map((data) => data.fond),
        first(),
      )
      .subscribe((fond) => {
        this.fond = fond;
      });

    this.treasuryService.getBank()
      .pipe(
        map((data) => data.expectedCav),
        first(),
      )
      .subscribe((expectedCav) => {
        this.balance = expectedCav;
      });
  }

  onSubmit() {
    // TODO
    console.log('onSubmit() à compléter');
  }

  toggleFundManagement() {
    this.showFundManagement = !this.showFundManagement;
  }
}
