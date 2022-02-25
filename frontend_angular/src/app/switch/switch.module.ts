import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {SwitchListComponent} from './switch-list/switch-list.component';
import {SwitchDetailsComponent} from './switch-details/switch-details.component';
import {SwitchEditComponent} from './switch-edit/switch-edit.component';
import {SwitchNewComponent} from './switch-new/switch-new.component';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';



@NgModule({
  declarations: [
    SwitchListComponent,
    SwitchDetailsComponent,
    SwitchEditComponent,
    SwitchNewComponent,
  ],
  imports: [
    NgxPaginationModule,
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: SwitchListComponent},
      {path: ':switch_id/view', component: SwitchDetailsComponent},
      {path: ':switch_id/edit', component: SwitchEditComponent},
      {path: 'add', component: SwitchNewComponent},
    ]),
    NgxPaginationModule,
  ]
})
export class SwitchModule { }