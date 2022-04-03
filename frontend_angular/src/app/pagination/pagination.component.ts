import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { PagingConf } from '../paging.config';

@Component({
  selector: 'app-pagination',
  templateUrl: './pagination.component.html',
  styleUrls: ['./pagination.component.sass']
})
export class PaginationComponent implements OnInit {
  @Input() maxItems: number | undefined;
  @Input() itemsPerPage: number = PagingConf.item_count;
  @Input() page: number = 1;

  @Output() pageChange = new EventEmitter<number>();

  deltaPage = 3;
  numberOfPages = 0;
  pagesBefore: Array<number> = [];
  pagesAfter: Array<number> = [];
  constructor() { }

  ngOnInit(): void {
    if (this.maxItems === undefined) {
      throw new Error("MaxItems should be specified in the pagination module");
    }
    if (this.itemsPerPage == 0) {
      throw new Error("At least one item per page should be shown");
    }
    this.numberOfPages = Math.ceil(this.maxItems / this.itemsPerPage);
    for (let i = 2; i <= ((this.numberOfPages > this.deltaPage) ? this.deltaPage : this.numberOfPages); i++) {
      this.pagesBefore.push(i);
    }
    for (let i = this.numberOfPages - this.deltaPage + 1; i <= this.numberOfPages - 1; i++) {
      this.pagesAfter.push(i);
    }
  }

  addPage(inc: number): void {
    if (!inc) {
      return
    }
    if (this.page + inc < 1) {
      this.page = 1;
    } else if (this.page + inc > this.numberOfPages) {
      this.page = this.numberOfPages;
    } else {
      this.page += inc;
    }
    this.pageChange.emit(this.page);
  }

  setPage(page: number): void {
    this.page = page;
    this.pageChange.emit(this.page);
  }
}
