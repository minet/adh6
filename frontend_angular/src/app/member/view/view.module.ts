import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CotisationComponent } from './cotisation/cotisation.component';
import { ViewComponent } from './view.component';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceModule } from '../../member-device/member-device-list.module';
import { AutoTroubleshootModule } from '../../auto-troubleshoot/auto-troubleshoot.module';



@NgModule({
  declarations: [
    CotisationComponent,
    ViewComponent
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([{ path: '', component: ViewComponent }]),
    MemberDeviceModule,
    AutoTroubleshootModule
  ],
})
export class ViewModule { }
