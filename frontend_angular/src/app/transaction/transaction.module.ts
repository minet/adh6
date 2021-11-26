import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {TransactionNewComponent} from './transaction-new/transaction-new.component';
import { RouterModule } from '@angular/router';
import { TransactionListComponent } from './transaction-list/transaction-list.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ModalModule } from 'ngx-bootstrap/modal';
import { CustomPaginationComponent } from '../custom-pagination.component';
import { ReactiveFormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    TransactionNewComponent,
    TransactionListComponent,
    CustomPaginationComponent,
  ],
  imports: [
    ReactiveFormsModule,
    FontAwesomeModule,
    CommonModule,
    RouterModule.forRoot([
      {path: '', redirectTo: 'add', pathMatch: 'full'},
      {path: 'add', component: TransactionNewComponent},
      {path: 'add/:account_id', component: TransactionNewComponent}
    ]),
    ModalModule.forRoot(),
  ]
})
export class TransactionModule { }
