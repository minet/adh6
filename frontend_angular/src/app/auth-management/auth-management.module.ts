import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';



@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: 'naina', loadChildren: () => import('./naina/naina.module').then(m => m.NainaModule) },
      { path: 'api-key', loadChildren: () => import('./api-key/api-key.module').then(m => m.ApiKeyModule) }
    ])
  ]
})
export class AuthManagementModule { }
