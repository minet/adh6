import { Route } from "@angular/router";

export const ROUTES: Route[] = [
  { 
    path: '', 
    loadComponent: () => import('./view.component').then(m => m.ViewComponent),
    children: [
      { path: 'profile', loadChildren: () => import('./details/routes').then(m => m.ROUTES) },
      { path: 'payment', loadComponent: () => import('./payment/payment.component').then(m => m.PaymentComponent) },
      { path: 'device', loadComponent: () => import('./devices/devices.component').then(m => m.DevicesComponent) },
    ]
  },
];