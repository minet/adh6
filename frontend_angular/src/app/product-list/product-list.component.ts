import { Component, OnInit } from '@angular/core';
import { Product, TreasuryService } from '../api';
import { SearchPage } from '../search-page';

@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.css']
})
export class ProductListComponent extends SearchPage<Product> implements OnInit {
  constructor(public treasuryService: TreasuryService) {
    super((terms, page) => this.treasuryService.productGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, 'response'));
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
