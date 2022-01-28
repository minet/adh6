import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MemberDeviceListComponent } from './member-device-list.component';



@NgModule({
  declarations: [
    MemberDeviceListComponent
  ],
  imports: [
    CommonModule
  ],
  exports: [
    MemberDeviceListComponent
  ]
})
export class MemberDeviceListModule { }
