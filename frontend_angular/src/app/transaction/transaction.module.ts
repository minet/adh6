import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {TransactionNewComponent} from './transaction-new/transaction-new.component';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ModalModule } from 'ngx-bootstrap/modal';
import { ReactiveFormsModule } from '@angular/forms';
import { TransactionListModule } from '../transaction-list/transaction-list.module';
import { ClickOutsideDirective } from './clickOutside.directive';



@NgModule({
  declarations: [
    TransactionNewComponent,
    ClickOutsideDirective,
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      {path: '', redirectTo: 'add', pathMatch: 'full'},
      {path: 'add', component: TransactionNewComponent},
      {path: 'add/:account_id', component: TransactionNewComponent}
    ]),
    ModalModule.forRoot(),
    TransactionListModule,
  ]
})
export class TransactionModule { }
