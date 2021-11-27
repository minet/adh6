import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { TreasuryComponent } from './treasury.component';
import { AccountModule } from '../account/account.module';



@NgModule({
  declarations: [
    TreasuryComponent,
  ],
  imports: [
    CommonModule,
    AccountModule,
    RouterModule.forChild([
      {path: '', component: TreasuryComponent},
    ])
  ]
})
export class TreasuryModule { }
