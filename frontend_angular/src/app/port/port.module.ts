import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ListComponent } from './list/list.component';
import { PortDetailsComponent } from './port-details/port-details.component';
import { PortNewComponent } from './port-new/port-new.component';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { PortListModule } from '../port-list/port-list.module';



@NgModule({
  declarations: [
    ListComponent,
    PortDetailsComponent,
    PortNewComponent,
  ],
  imports: [
    FormsModule,
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      { path: '', redirectTo: 'search', pathMatch: 'full' },
      { path: 'search', component: ListComponent },
      { path: ':switch_id/:port_id', component: PortDetailsComponent },
      { path: ':switch_id/add', component: PortNewComponent },
    ]),
    PortListModule
  ]
})
export class PortModule { }
