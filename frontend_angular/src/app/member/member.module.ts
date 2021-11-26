import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {MemberListComponent} from './member-list/member-list.component';
import {MemberCreateOrEditComponent} from './member-create-or-edit/member-create-or-edit.component';
import {MemberViewComponent} from './member-view/member-view.component';
import {MemberPasswordEditComponent} from './member-password-edit/member-password-edit.component';
import { RouterModule } from '@angular/router';
import { CotisationComponent } from './cotisation/cotisation.component';
import { ReactiveFormsModule } from '@angular/forms';
import { CustomPaginationComponent } from '../custom-pagination.component';



@NgModule({
  declarations: [
    MemberCreateOrEditComponent,
    MemberCreateOrEditComponent,
    MemberPasswordEditComponent,
    MemberListComponent,
    MemberViewComponent,
    CotisationComponent,
    CustomPaginationComponent,
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forRoot([
      {path: 'search', component: MemberListComponent},
      {path: 'add', component: MemberCreateOrEditComponent},
      {path: 'view/:member_id', component: MemberViewComponent},
      {path: 'edit/:member_id', component: MemberCreateOrEditComponent},
      {path: 'password/:member_id', component: MemberPasswordEditComponent}
    ])
  ]
})
export class MemberModule { }
