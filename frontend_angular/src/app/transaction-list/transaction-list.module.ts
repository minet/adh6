import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionListComponent } from './transaction-list.component';
import { PaginationModule } from '../pagination/pagination.module';



@NgModule({
  declarations: [
    TransactionListComponent,
  ],
  imports: [
    CommonModule,
    PaginationModule
  ],
  exports: [
    TransactionListComponent
  ]
})
export class TransactionListModule { }
