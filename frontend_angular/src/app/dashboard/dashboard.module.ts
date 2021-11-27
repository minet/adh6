import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { MemberDeviceListComponent } from './member-device-list/member-device-list.component';
import { DeviceNewComponent } from './device-new/device-new.component';
import { MacVendorComponent } from './mac-vendor/mac-vendor.component';
import { ReactiveFormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    DashboardComponent,
    MemberDeviceListComponent,
    DeviceNewComponent,
    MacVendorComponent,
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forRoot([
      {path: '', component: DashboardComponent}
    ])
  ]
})
export class DashboardModule { }
