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
    RouterModule.forRoot([
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: SwitchListComponent},
      {path: 'view/:switch_id', component: SwitchDetailsComponent},
      {path: 'edit/:switch_id', component: SwitchEditComponent},
      {path: 'add', component: SwitchNewComponent},
    ])
  ]
})
export class SwitchModule { }
