import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NainaComponent } from './naina.component';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    NainaComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: "", component: NainaComponent }
    ]),
    FormsModule
  ]
})
export class NainaModule { }
