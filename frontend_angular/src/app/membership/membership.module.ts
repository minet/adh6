import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MembershipListComponent } from './membership-list/membership-list.component';
import { NgxPaginationModule } from 'ngx-pagination';



@NgModule({
  declarations: [
    MembershipListComponent,
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([
      {path: '', component: MembershipListComponent},
    ]),
    NgxPaginationModule,
  ]
})
export class MembershipModule { }
