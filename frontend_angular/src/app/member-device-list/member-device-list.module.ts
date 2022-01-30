import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MemberDeviceListComponent } from './member-device-list.component';
import { MacVendorComponent } from './mac-vendor/mac-vendor.component';



@NgModule({
  declarations: [
    MemberDeviceListComponent,
    MacVendorComponent
  ],
  imports: [
    CommonModule
  ],
  exports: [
    MemberDeviceListComponent
  ]
})
export class MemberDeviceListModule { }
