import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ListComponent } from './list.component';
import { RouterModule } from '@angular/router';
import { PaginationModule } from '../../pagination/pagination.module';

@NgModule({
  declarations: [
    ListComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([{ path: '', component: ListComponent }]),
    PaginationModule
  ]
})
export class ListModule { }
