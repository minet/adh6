import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';

import {DashboardComponent} from './dashboard/dashboard.component';
import {MemberListComponent} from './member-list/member-list.component';
import {MemberCreateOrEditComponent} from './member-create-or-edit/member-create-or-edit.component';
import {MemberViewComponent} from './member-view/member-view.component';
import {RoomListComponent} from './room-list/room-list.component';
import {RoomDetailsComponent} from './room-details/room-details.component';
import {RoomEditComponent} from './room-edit/room-edit.component';
import {RoomNewComponent} from './room-new/room-new.component';
import {PortListComponent} from './port-list/port-list.component';
import {PortDetailsComponent} from './port-details/port-details.component';
import {PortNewComponent} from './port-new/port-new.component';
import {SwitchLocalComponent} from './switch-local/switch-local.component';
import {SwitchListComponent} from './switch-list/switch-list.component';
import {SwitchDetailsComponent} from './switch-details/switch-details.component';
import {SwitchEditComponent} from './switch-edit/switch-edit.component';
import {SwitchNewComponent} from './switch-new/switch-new.component';
import {DeviceListComponent} from './device-list/device-list.component';
import {MemberPasswordEditComponent} from './member-password-edit/member-password-edit.component';
import {TreasuryComponent} from './treasury/treasury.component';
import {AccountCreateComponent} from './account-create/account-create.component';
import {TransactionNewComponent} from './transaction-new/transaction-new.component';
import {AccountViewComponent} from './account-view/account-view.component';
import {AccountEditComponent} from './account-edit/account-edit.component';
import {ProductListComponent} from './product-list/product-list.component';
import {AccountListComponent} from './account-list/account-list.component';
import {AuthorizeComponent} from './authorize/authorize.component';
import {PortailComponent} from './portail/portail.component';

const routes: Routes = [
  {path: '', redirectTo: '/dashboard', pathMatch: 'full'},
  {path: 'dashboard', component: DashboardComponent},
  {path: 'authorize', component: AuthorizeComponent,
    data: {
    bypassAuth: true
  }},
  {path: 'portail', component: PortailComponent,
    data: {
    bypassAuth: true
  }},
  {
    path: 'member',
    children: [
      {path: 'search', component: MemberListComponent},
      {path: 'add', component: MemberCreateOrEditComponent},
      {path: 'view/:member_id', component: MemberViewComponent},
      {path: 'edit/:member_id', component: MemberCreateOrEditComponent},
      {path: 'password/:member_id', component: MemberPasswordEditComponent},
    ],
  },
  {
    path: 'room',
    children: [
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: RoomListComponent},
      {path: 'add', component: RoomNewComponent},
      {path: 'view/:room_id', component: RoomDetailsComponent},
      {path: 'edit/:room_id', component: RoomEditComponent},
    ],
  },
  {
    path: 'device',
    children: [
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: DeviceListComponent},
    ],
  },
  {path: 'switch_local', component: SwitchLocalComponent},
  {
    path: 'switch',
    children: [
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: SwitchListComponent},
      {path: 'view/:switch_id', component: SwitchDetailsComponent},
      {path: 'edit/:switch_id', component: SwitchEditComponent},
      {path: 'add', component: SwitchNewComponent},
      {path: 'view/:switch_id/port/:port_id', component: PortDetailsComponent},
      {path: 'add/:switch_id/port', component: PortNewComponent},
    ],
  },
  {
    path: 'port',
    children: [
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: PortListComponent},
    ],
  },
  {
    path: 'treasury',
    children: [
      {path: '', component: TreasuryComponent},
    ]
  },
  {
    path: 'account',
    children: [
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: AccountListComponent},
      {path: 'add', component: AccountCreateComponent},
      {path: 'view/:account_id', component: AccountViewComponent},
      {path: 'edit/:account_id', component: AccountEditComponent},
    ]
  },
  {
    path: 'transaction',
    children: [
      {path: '', redirectTo: 'add', pathMatch: 'full'},
      {path: 'add', component: TransactionNewComponent},
      {path: 'add/:account_id', component: TransactionNewComponent}
    ]
  },
  {
    path: 'product',
    children: [
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: ProductListComponent},
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
