import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {TransactionNewComponent} from "./transaction-new/transaction-new.component";
import {TransactionExportComponent} from "./transaction-export/transaction-export.component";
import {RouterModule} from "@angular/router";
import {ReactiveFormsModule} from "@angular/forms";
import {ClickOutsideDirective} from "./clickOutside.directive";
import {TransactionListComponent} from "../transaction-list/transaction-list.component";

@NgModule({
  declarations: [],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    TransactionNewComponent,
    TransactionExportComponent,
    ClickOutsideDirective,
    RouterModule.forChild([
      {path: "", redirectTo: "add", pathMatch: "full"},
      {path: "add", component: TransactionNewComponent},
      {path: "export", component: TransactionExportComponent},
    ]),
    TransactionListComponent,
  ],
})
export class TransactionModule {}
