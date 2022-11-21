import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'portail', loadComponent: () => import('./portail/portail.component').then(m => m.PortailComponent) },
  { path: 'password/:member_id/:creation', loadComponent: () => import('./member-password-edit/member-password-edit.component').then(m => m.MemberPasswordEditComponent) },
  { path: 'product', loadChildren: () => import('./product-list/product-list.module').then(m => m.ProductListModule) },
  { path: 'dashboard', loadChildren: () => import('./dashboard/routes').then(m => m.ROUTES) },
  { path: 'account', loadChildren: () => import('./account/routes').then(m => m.ROUTES) },
  { path: 'switch', loadChildren: () => import('./switch/switch.module').then(m => m.SwitchModule) },
  { path: 'port', loadChildren: () => import('./port/routes').then(m => m.ROUTES) },
  { path: 'room', loadChildren: () => import('./room/room.module').then(m => m.RoomModule) },
  { path: 'transaction', loadChildren: () => import('./transaction/transaction.module').then(m => m.TransactionModule) },
  { path: 'treasury', loadComponent: () => import('./treasury/treasury.component').then(m => m.TreasuryComponent) },
  { path: 'member', loadChildren: () => import('./member/member.module').then(m => m.MemberModule) },
  { path: 'device', loadComponent: () => import('./device/device-list.component').then(m => m.DeviceListComponent) },
  { path: 'switch_local', loadComponent: () => import('./switch-local/switch-local.component').then(m => m.SwitchLocalComponent) },
  { path: 'auth', loadChildren: () => import('./auth-management/routes').then(m => m.ROUTES) },
  { path: '**', redirectTo: '/dashboard' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
