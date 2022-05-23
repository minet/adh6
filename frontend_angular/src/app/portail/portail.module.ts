import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PortailComponent } from './portail.component';
import { RouterModule } from '@angular/router';


@NgModule({
  declarations: [
    PortailComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([{ path: '', component: PortailComponent }])
  ]
})
export class PortailModule { }
