import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CotisationComponent } from './cotisation/cotisation.component';
import { ViewComponent } from './view.component';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceModule } from '../../member-device/member-device-list.module';
import { AutoTroubleshootModule } from '../../auto-troubleshoot/auto-troubleshoot.module';
import { AbilityModule } from '@casl/angular';



@NgModule({
  declarations: [
    CotisationComponent,
    ViewComponent
  ],
  imports: [
    ReactiveFormsModule,
    FormsModule,
    CommonModule,
    RouterModule.forChild([{ path: '', component: ViewComponent }]),
    MemberDeviceModule,
    AutoTroubleshootModule,
    AbilityModule,
  ],
})
export class ViewModule { }
