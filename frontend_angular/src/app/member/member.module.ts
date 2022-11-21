import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: '', redirectTo: 'search', pathMatch: 'full' },
      { path: 'search', loadComponent: () => import('./list/list.component').then(m => m.ListComponent) },
      { path: 'add', loadComponent: () => import('./create-or-edit/create-or-edit.component').then(m => m.CreateOrEditComponent) },
      { path: 'view/:member_id', loadChildren: () => import('./view/routes').then(m => m.ROUTES) },
      { path: 'edit/:member_id', loadComponent: () => import('./create-or-edit/create-or-edit.component').then(m => m.CreateOrEditComponent) },
    ]),
  ]
})
export class MemberModule { }
