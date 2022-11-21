import { Route } from "@angular/router";

export const ROUTES: Route[] = [
  { path: '', redirectTo: 'search', pathMatch: 'full' },
  { path: 'search', loadComponent: () => import('./list/list.component').then(c => c.PortListComponent) },
  { path: ':switch_id/:port_id', loadComponent: () => import('./port-details/port-details.component').then(c => c.PortDetailsComponent) }
]