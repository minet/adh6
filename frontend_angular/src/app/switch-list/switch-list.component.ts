import {Component, OnInit} from '@angular/core';

import {Observable} from 'rxjs';

import {ModelSwitch, SwitchService} from '../api';
import {PagingConf} from '../paging.config';
import {SearchPage} from '../search-page';
import {map} from 'rxjs/operators';

export interface SwitchListResult {
  switches: Array<ModelSwitch>;
  item_count?: number;
  current_page?: number;
  items_per_page?: number;
}

@Component({
  selector: 'app-switch-list',
  templateUrl: './switch-list.component.html',
  styleUrls: ['./switch-list.component.css']
})
export class SwitchListComponent extends SearchPage implements OnInit {

  result$: Observable<SwitchListResult>;

  constructor(public switchService: SwitchService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.result$ = this.getSearchResult((terms, page) => this.fetchSwitches(terms, page));
  }

  private fetchSwitches(terms: string, page: number): Observable<SwitchListResult> {
    const n = +PagingConf.item_count;
    return this.switchService.switchGet(n, (page - 1) * n, terms, undefined, 'response')
      .pipe(
        map((response) => {
          return <SwitchListResult>{
            switches: response.body,
            item_count: +response.headers.get('x-total-count'),
            current_page: page,
            items_per_page: n,
          };
        }),
      );
  }
}
