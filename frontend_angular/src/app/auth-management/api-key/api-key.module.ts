import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiKeyComponent } from './api-key.component';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    ApiKeyComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: '', component: ApiKeyComponent }
    ]),
    FormsModule
  ]
})
export class ApiKeyModule { }
