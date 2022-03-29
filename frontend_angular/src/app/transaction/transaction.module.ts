import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionNewComponent } from './transaction-new/transaction-new.component';
import { RouterModule } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ReactiveFormsModule } from '@angular/forms';
import { TransactionListModule } from '../transaction-list/transaction-list.module';
import { ClickOutsideDirective } from './clickOutside.directive';
import { AccountSearchComponent } from './account-search/account-search.component';



@NgModule({
  declarations: [
    TransactionNewComponent,
    ClickOutsideDirective,
    AccountSearchComponent,
  ],
  imports: [
    ReactiveFormsModule,
    FontAwesomeModule,
    CommonModule,
    RouterModule.forChild([
      { path: '', redirectTo: 'add', pathMatch: 'full' },
      { path: 'add', component: TransactionNewComponent },
      { path: 'add/:account_id', component: TransactionNewComponent }
    ]),
    TransactionListModule,
  ]
})
export class TransactionModule { }
