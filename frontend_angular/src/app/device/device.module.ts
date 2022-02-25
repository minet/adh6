import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {DeviceListComponent} from './device-list/device-list.component';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';



@NgModule({
  declarations: [
    DeviceListComponent,
  ],
  imports: [
    NgxPaginationModule,
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: DeviceListComponent},
    ])
  ]
})
export class DeviceModule { }