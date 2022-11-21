import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionNewComponent } from './transaction-new/transaction-new.component';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { ClickOutsideDirective } from './clickOutside.directive';
import { AccountSearchComponent } from './transaction-new/account-search/account-search.component';
import { TransactionListComponent } from '../transaction-list/transaction-list.component';



@NgModule({
  declarations: [
    TransactionNewComponent,
    ClickOutsideDirective,
    AccountSearchComponent,
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      { path: '', redirectTo: 'add', pathMatch: 'full' },
      { path: 'add', component: TransactionNewComponent },
      { path: 'add/:account_id', component: TransactionNewComponent }
    ]),
    TransactionListComponent,
  ]
})
export class TransactionModule { }
