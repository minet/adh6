import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { TreasuryComponent } from './treasury.component';



@NgModule({
  declarations: [
    TreasuryComponent,
  ],
  imports: [
    CommonModule,
    RouterModule.forRoot([
      {path: '', component: TreasuryComponent},    ])
  ]
})
export class TreasuryModule { }
