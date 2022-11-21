import { Route } from '@angular/router';

export const ROUTES: Route[] = [
    { path: '', redirectTo: 'search', pathMatch: 'full' },
    { path: 'search', loadComponent: () => import('./account-list/account-list.component').then(c => c.AccountListComponent) },
    { path: 'add', loadComponent: () => import('./account-create/account-create.component').then(c => c.AccountCreateComponent) },
    { path: 'view/:account_id', loadComponent: () => import('./account-view/account-view.component').then(c => c.AccountViewComponent) },
    { path: 'edit/:account_id', loadComponent: () => import('./account-edit/account-edit.component').then(c => c.AccountEditComponent) }
]