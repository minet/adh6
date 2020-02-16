import {Component, OnInit} from '@angular/core';

import {Observable} from 'rxjs';

import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import {AccountService, InlineResponse200} from '../api';
import {Account} from '../api';
import {PagingConf} from '../paging.config';

import {map} from 'rxjs/operators';
import {SearchPage} from '../search-page';
import { AccountType } from '../api';
import { AccountTypeService } from '../api';
import {CaisseService} from '../api';
import {InlineResponse2002} from '../api/model/inlineResponse2002';

@Component({
  selector: 'app-treasury',
  templateUrl: './treasury.component.html',
  styleUrls: ['./treasury.component.css']
})
export class TreasuryComponent implements OnInit {
  caisse$: Observable<InlineResponse2002>;

  showFundManagement = false;
  fundManagementForm: FormGroup;
  create = false;

  constructor(
    private fb: FormBuilder,
    public caisseService: CaisseService,
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
    this.caisse$ = this.caisseService.caisseGet();
  }

  onSubmit() {
    // TODO
    console.log('onSubmit() à compléter');
  }

  toggleFundManagement() {
    this.showFundManagement = !this.showFundManagement;
  }
}
