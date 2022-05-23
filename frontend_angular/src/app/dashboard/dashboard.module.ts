import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceModule } from '../member-device/member-device-list.module';
import { AutoTroubleshootModule } from '../auto-troubleshoot/auto-troubleshoot.module';



@NgModule({
  declarations: [
    DashboardComponent
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      { path: '', component: DashboardComponent }
    ]),
    MemberDeviceModule,
    AutoTroubleshootModule
  ]
})
export class DashboardModule { }
