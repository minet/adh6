import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MembershipListComponent } from './membership-list/membership-list.component';
import { CustomPaginationComponent } from '../custom-pagination.component';



@NgModule({
  declarations: [
    MembershipListComponent,
    CustomPaginationComponent,
  ],
  imports: [
    CommonModule,
    RouterModule.forRoot([
      {path: '', component: MembershipListComponent},
    ])
  ]
})
export class MembershipModule { }
