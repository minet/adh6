import {Component, OnInit} from '@angular/core';

import {BehaviorSubject, Observable} from 'rxjs';
import {ActivatedRoute} from '@angular/router';

import {AbstractPort, ModelSwitch, Port, PortService, SwitchService} from '../../api';

import {SearchPage} from '../../search-page';
import {PagingConf} from '../../paging.config';

import {map} from 'rxjs/operators';

export interface PortListResult {
  ports: Array<Port>;
  item_count?: number;
  current_page?: number;
  items_per_page?: number;
}

@Component({
  selector: 'app-switch-details',
  templateUrl: './switch-details.component.html',
  styleUrls: ['./switch-details.component.css']
})
export class SwitchDetailsComponent extends SearchPage implements OnInit {

  switch$: Observable<ModelSwitch>;
  result$: Observable<PortListResult>;
  switch_id: number;
  page_number = 1;
  item_count = 1;
  items_per_page: number = +PagingConf.item_count;
  private searchTerms = new BehaviorSubject<string>('');

  constructor(public switchService: SwitchService, private route: ActivatedRoute, public portService: PortService) {
    super();
  }

  search(term: string): void {
    this.searchTerms.next(term);
  }

  ngOnInit() {
    super.ngOnInit();
    this.route.params.subscribe(params => {
      this.switch_id = +params['switch_id'];
      this.switch$ = this.switchService.switchSwitchIdGet(this.switch_id);
      this.result$ = this.getSearchResult((terms, page) => this.fetchPorts(terms, page));
    });
  }

  private fetchPorts(terms: string, page: number): Observable<PortListResult> {
    const n = +PagingConf.item_count;
    return this.portService.portGet(n, (page - 1) * n, terms, <AbstractPort>{switchObj: this.switch_id}, 'response')
      .pipe(
        map((response) => <PortListResult>{
          ports: response.body,
          item_count: +response.headers.get('x-total-count'),
          current_page: page,
          items_per_page: n,
        }),
      );
  }

  handlePageChange(page: number) {
    this.changePage(page);
    console.log(page);
    this.result$ = this.getSearchResult((terms, page) => this.fetchPorts(terms, page));
  }
}
