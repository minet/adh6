import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionListComponent } from './transaction-list.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { PaginationModule } from '../pagination/pagination.module';



@NgModule({
  declarations: [
    TransactionListComponent,
  ],
  imports: [
    CommonModule,
    FontAwesomeModule,
    NgxPaginationModule,
    PaginationModule
  ],
  exports: [
    TransactionListComponent
  ]
})
export class TransactionListModule { }
