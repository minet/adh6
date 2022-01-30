import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { DeviceNewComponent } from './device-new/device-new.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceListModule } from '../member-device-list/member-device-list.module';



@NgModule({
  declarations: [
    DashboardComponent,
    DeviceNewComponent,
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forRoot([
      {path: '', component: DashboardComponent}
    ]),
    MemberDeviceListModule
  ]
})
export class DashboardModule { }
