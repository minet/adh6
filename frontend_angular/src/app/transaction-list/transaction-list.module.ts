import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionListComponent } from './transaction-list.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';



@NgModule({
  declarations: [
    TransactionListComponent,
  ],
  imports: [
    CommonModule,
    FontAwesomeModule,
    NgxPaginationModule,
  ],
  exports: [
    TransactionListComponent
  ]
})
export class TransactionListModule { }
