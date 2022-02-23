import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {MemberListComponent} from './member-list/member-list.component';
import {MemberCreateOrEditComponent} from './member-create-or-edit/member-create-or-edit.component';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';



@NgModule({
  declarations: [
    MemberCreateOrEditComponent,
    MemberCreateOrEditComponent,
    MemberListComponent,
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      {path: 'search', component: MemberListComponent},
      {path: 'add', component: MemberCreateOrEditComponent},
      {path: 'view/:member_id', loadChildren: () => import('./member-view/member-view.module').then(m => m.MemberViewModule)},
      {path: 'edit/:member_id', component: MemberCreateOrEditComponent},
    ]),
    NgxPaginationModule,
  ]
})
export class MemberModule { }
