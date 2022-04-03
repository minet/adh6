import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PortListComponent } from './port-list.component';
import { PaginationModule } from '../pagination/pagination.module';
import { RouterModule } from '@angular/router';



@NgModule({
  declarations: [
    PortListComponent
  ],
  imports: [
    CommonModule,
    PaginationModule,
    RouterModule
  ],
  exports: [
    PortListComponent,
  ]
})
export class PortListModule { }
