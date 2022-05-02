import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { CreateOrEditComponent } from './create-or-edit.component';



@NgModule({
  declarations: [
    CreateOrEditComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule.forChild([{ path: '', component: CreateOrEditComponent }])
  ]
})
export class CreateOrEditModule { }
