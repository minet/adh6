import { Route } from "@angular/router";

export const ROUTES: Route[] = [
    { 
        path: '', 
        loadComponent: () => import('./dashboard.component').then(c => c.DashboardComponent),
        data: { animation: 0 },
        children: [
            {
                path: 'device',
                loadComponent: () => import('./tab-device.component').then(m => m.DeviceComponent),
                data: { animation: 0 }
            },
            {
                path: 'profile',
                loadComponent: () => import('./tab-account.component').then(c => c.AccountComponent),
                data: { animation: 1 }
            }
        ]
    },
]