import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ViewComponent } from './view.component';
import { RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceModule } from '../../member-device/member-device-list.module';
import { AutoTroubleshootModule } from '../../auto-troubleshoot/auto-troubleshoot.module';
import { AbilityModule } from '@casl/angular';
import { MailinglistModule } from '../../mailinglist/mailinglist.module';
import { CotisationComponent } from './cotisation/cotisation.component';
import { BuyProductComponent } from './buy-product/buy-product.component';
import { BuyComponent } from './buy/buy.component';



@NgModule({
  declarations: [
    ViewComponent,
    BuyProductComponent,
    CotisationComponent,
    BuyComponent,
  ],
  imports: [
    ReactiveFormsModule,
    FormsModule,
    CommonModule,
    RouterModule.forChild([{ path: '', component: ViewComponent }]),
    MemberDeviceModule,
    AutoTroubleshootModule,
    AbilityModule,
    MailinglistModule,
  ],
  entryComponents: [
    BuyComponent
  ]
})
export class ViewModule { }
