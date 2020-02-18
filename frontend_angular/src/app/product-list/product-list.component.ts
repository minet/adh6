import {Component, OnInit} from '@angular/core';

import {Observable} from 'rxjs';

import {Product, TreasuryService} from '../api';
import {PagingConf} from '../paging.config';
import {SearchPage} from '../search-page';
import {map} from 'rxjs/operators';

export interface ProductListResult {
  products: Array<Product>;
  item_count?: number;
  current_page?: number;
  items_per_page?: number;
}

@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.css']
})
export class ProductListComponent extends SearchPage implements OnInit {
  result$: Observable<ProductListResult>;

  constructor(public treasuryService: TreasuryService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.result$ = this.getSearchResult((terms, page) => this.fetchProducts(terms, page));
  }

  private fetchProducts(terms: string, page: number): Observable<ProductListResult> {
      const n = +PagingConf.item_count;
      return this.treasuryService.productGet(n, (page - 1) * n, terms, 'response')
        .pipe(
          map((response) => {
            return <ProductListResult> {
              products: response.body,
              item_count: +response.headers.get('x-total-count'),
              current_page: page,
              items_per_page: n,
            };
          }),
        );
  }
}
