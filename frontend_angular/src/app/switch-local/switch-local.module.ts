import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { SwitchLocalComponent } from './switch-local.component';



@NgModule({
  declarations: [
    SwitchLocalComponent,
  ],
  imports: [
    CommonModule,
    RouterModule.forRoot([
      {path: '', component: SwitchLocalComponent}
    ])
  ]
})
export class SwitchLocalModule { }
