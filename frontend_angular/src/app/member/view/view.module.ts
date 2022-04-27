import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CotisationComponent } from './cotisation/cotisation.component';
import { ViewComponent } from './view.component';
import { RedirectGuard } from './redirect-guard/redirect-guard';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceModule } from '../../member-device/member-device-list.module';



@NgModule({
  declarations: [
    CotisationComponent,
    ViewComponent
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      { path: '', component: ViewComponent },
      {
        path: 'charter',
        canActivate: [RedirectGuard],
        component: RedirectGuard,
        data: {
          externalUrl: 'https://chartes.minet.net'
        }
      },
    ]),
    MemberDeviceModule
  ],
  providers: [
    RedirectGuard,
  ]
})
export class ViewModule { }
