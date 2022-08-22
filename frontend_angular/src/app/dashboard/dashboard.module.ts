import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceModule } from '../member-device/member-device-list.module';
import { AutoTroubleshootModule } from '../auto-troubleshoot/auto-troubleshoot.module';
import { DeviceComponent } from './tabs/device.component';
import { MailinglistModule } from '../mailinglist/mailinglist.module';
import { AccountComponent } from './tabs/account.component';
import { RenewalAndPasswordComponent } from './renewal-and-password/renewal-and-password.component';


@NgModule({
  declarations: [
    DashboardComponent,
    DeviceComponent,
    AccountComponent,
    RenewalAndPasswordComponent
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      { path: '', component: DashboardComponent }
    ]),
    MemberDeviceModule,
    AutoTroubleshootModule,
    MailinglistModule
  ],
})
export class DashboardModule { }
