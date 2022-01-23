import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CotisationComponent } from './cotisation/cotisation.component';
import { MemberViewComponent } from './member-view.component';
import { RedirectGuard } from './redirect-guard/redirect-guard';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { MemberDeviceListModule } from '../../member-device-list/member-device-list.module';



@NgModule({
  declarations: [
    CotisationComponent,
    MemberViewComponent
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      {path: '', component: MemberViewComponent},
      {
        path: 'charter',
        canActivate: [RedirectGuard],
        component: RedirectGuard,
        data: {
          externalUrl: 'https://chartes.minet.net'
        }
      },
    ]),
    MemberDeviceListModule
  ],
  providers: [
    RedirectGuard,
  ]
})
export class MemberViewModule { }
