import { Route } from '@angular/router'

export const ROUTES: Route[] = [
  { path: 'naina', loadComponent: () => import('./naina.component').then(m => m.NainaComponent) },
  { path: 'api-key', loadComponent: () => import('./api-key.component').then(m => m.ApiKeyComponent) }
]
