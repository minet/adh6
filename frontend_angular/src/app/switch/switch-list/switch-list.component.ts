import { Component, OnInit } from '@angular/core';

import { Observable, of } from 'rxjs';

import { ModelSwitch, SwitchService } from '../../api';
import { PagingConf } from '../../paging.config';
import { SearchPage } from '../../search-page';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-switch-list',
  templateUrl: './switch-list.component.html',
  styleUrls: ['./switch-list.component.css']
})
export class SwitchListComponent extends SearchPage implements OnInit {
  maxItems$: Observable<number>;
  result$: Observable<Array<ModelSwitch>>;

  constructor(public switchService: SwitchService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.maxItems$ = this.getSearchHeader((terms) => this.switchService.switchHead(1, 0, terms, undefined, 'response').pipe(map((response) => { return (response) ? +response.headers.get("x-total-count") : 0 })));
    this.result$ = this.getSearchResult((terms, page) => this.fetchSwitches(terms, page));
  }

  private fetchSwitches(terms: string, page: number): Observable<Array<ModelSwitch>> {
    const n = +PagingConf.item_count;
    return this.switchService.switchGet(n, (page - 1) * n, terms);
  }

  handlePageChange(page: number) {
    this.changePage(page);
    this.result$ = this.getSearchResult((terms, page) => this.fetchSwitches(terms, page));
  }
}
