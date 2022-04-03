import { Component, Input, OnInit } from '@angular/core';

import { Observable } from 'rxjs';

import { AbstractPort, Port, PortService } from '../api';
import { PagingConf } from '../paging.config';

import { map } from 'rxjs/operators';
import { SearchPage } from '../search-page';

@Component({
  selector: 'app-port-list',
  templateUrl: './port-list.component.html',
  styleUrls: ['./port-list.component.css']
})
export class PortListComponent extends SearchPage implements OnInit {
  maxItems$: Observable<number>;
  result$: Observable<Array<Port>>;

  @Input() switchId: number | undefined;

  private filter: AbstractPort | undefined;
  constructor(public portService: PortService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.filter = (this.switchId) ? <AbstractPort>{ switchObj: this.switchId } : undefined;
    this.maxItems$ = this.getSearchHeader((terms) => this.portService.portHead(1, 0, terms, this.filter, 'response').pipe(map((response) => { return (response) ? +response.headers.get("x-total-count") : 0 })))
    this.result$ = this.getSearchResult((terms, page) => this.fetchPort(terms, page));
  }

  private fetchPort(terms: string, page: number): Observable<Array<Port>> {
    const n = +PagingConf.item_count;
    return this.portService.portGet(n, (page - 1) * n, terms, this.filter);
  }

  handlePageChange(page: number) {
    this.changePage(page);
    this.result$ = this.getSearchResult((terms, page) => this.fetchPort(terms, page));
  }
}
