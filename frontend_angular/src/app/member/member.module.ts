import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';



@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: 'search', loadChildren: () => import('./list/list.module').then(m => m.ListModule) },
      { path: 'add', loadChildren: () => import('./create-or-edit/create-or-edit.module').then(m => m.CreateOrEditModule) },
      { path: 'view/:member_id', loadChildren: () => import('./view/view.module').then(m => m.ViewModule) },
      { path: 'edit/:member_id', loadChildren: () => import('./create-or-edit/create-or-edit.module').then(m => m.CreateOrEditModule) },
    ])
  ]
})
export class MemberModule { }
