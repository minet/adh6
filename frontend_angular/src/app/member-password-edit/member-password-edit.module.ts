import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MemberPasswordEditComponent } from './member-password-edit.component';
import { RouterModule } from '@angular/router';



@NgModule({
  declarations: [
    MemberPasswordEditComponent,
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule.forChild([
      { path: '', component: MemberPasswordEditComponent }
    ])
  ]
})
export class MemberPasswordEditModule { }
