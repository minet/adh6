import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionListComponent } from './transaction-list.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { ReactiveFormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    TransactionListComponent,
  ],
  imports: [
    CommonModule,
    NgxPaginationModule,
  ],
  exports: [
    TransactionListComponent
  ]
})
export class TransactionListModule { }
