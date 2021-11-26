import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {PortListComponent} from './port-list/port-list.component';
import {PortDetailsComponent} from './port-details/port-details.component';
import {PortNewComponent} from './port-new/port-new.component';
import { RouterModule } from '@angular/router';
import { CustomPaginationComponent } from '../custom-pagination.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    PortListComponent,
    PortDetailsComponent,
    PortNewComponent,
    CustomPaginationComponent,
  ],
  imports: [
    FormsModule,
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forRoot([
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: PortListComponent},
      {path: 'port/:switch_id/:port_id', component: PortDetailsComponent},
      {path: 'port/:switch_id/add', component: PortNewComponent},
    ])
  ]
})
export class PortModule { }
