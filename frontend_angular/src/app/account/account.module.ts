import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AccountViewComponent } from './account-view/account-view.component';
import { AccountEditComponent } from './account-edit/account-edit.component';
import { AccountListComponent } from './account-list/account-list.component';
import { AccountCreateComponent } from './account-create/account-create.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ObjectFilterPipe } from './ObjectFilter.pipe';
import { TransactionListModule } from '../transaction-list/transaction-list.module';
import { PaginationModule } from '../pagination/pagination.module';


@NgModule({
  declarations: [
    AccountCreateComponent,
    AccountViewComponent,
    AccountEditComponent,
    AccountListComponent,
    ObjectFilterPipe,
  ],
  imports: [
    CommonModule,
    TransactionListModule,
    FormsModule,
    ReactiveFormsModule,
    FontAwesomeModule,
    RouterModule.forChild([
      { path: '', redirectTo: 'search', pathMatch: 'full' },
      { path: 'search', component: AccountListComponent },
      { path: 'add', component: AccountCreateComponent },
      { path: 'view/:account_id', component: AccountViewComponent },
      { path: 'edit/:account_id', component: AccountEditComponent }
    ]),
    PaginationModule
  ],
  exports: [
    AccountListComponent,
  ]
})
export class AccountModule { }
