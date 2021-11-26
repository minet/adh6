import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';

import {ProductListComponent} from './product-list/product-list.component';
import {PortailComponent} from './portail/portail.component';
import {RedirectGuard} from './redirect-guard/redirect-guard';

const routes: Routes = [
  {path: '', redirectTo: '/dashboard', pathMatch: 'full'},
  {
    path: 'portail', component: PortailComponent,
    data: {
      bypassAuth: true
    }
  },
  {
    path: 'charter',
    canActivate: [RedirectGuard],
    component: RedirectGuard,
    data: {
      externalUrl: 'https://chartes.minet.net'
    }
  },
  {
    path: 'product',
    children: [
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: ProductListComponent},
    ]
  },
  {path: 'dashboard', loadChildren: () => import('./dashboard/dashboard.module').then(m => m.DashboardModule)},
  {path: 'account', loadChildren: () => import('./account/account.module').then(m => m.AccountModule)},
  {path: 'switch', loadChildren: () => import('./switch/switch.module').then(m => m.SwitchModule)},
  {path: 'port', loadChildren: () => import('./port/port.module').then(m => m.PortModule)},
  {path: 'room', loadChildren: () => import('./room/room.module').then(m => m.RoomModule)},
  {path: 'transaction', loadChildren: () => import('./transaction/transaction.module').then(m => m.TransactionModule)},
  //{path: 'treasury', loadChildren: () => import('./treasury/treasury.module').then(m => m.TreasuryModule)},
  {path: 'membership', loadChildren: () => import('./membership/membership.module').then(m => m.MembershipModule)},
  {path: 'member', loadChildren: () => import('./member/member.module').then(m => m.MemberModule)},
  {path: 'device', loadChildren: () => import('./device/device.module').then(m => m.DeviceModule)},
  {path: 'switch_local', loadChildren: () => import('./switch-local/switch-local.module').then(m => m.SwitchLocalModule)},
  {path: '**', redirectTo: '/dashboard'},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
