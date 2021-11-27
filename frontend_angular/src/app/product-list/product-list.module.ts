import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProductListComponent } from './product-list.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { RouterModule } from '@angular/router';

@NgModule({
  declarations: [
    ProductListComponent
  ],
  imports: [
    CommonModule,
    NgxPaginationModule,
    RouterModule.forChild([
      {path: '', redirectTo: 'search', pathMatch: 'full'},
      {path: 'search', component: ProductListComponent},
    ])
  ]
})
export class ProductListModule { }
