import { Component, OnInit } from '@angular/core';

import { Device, DeviceService } from '../../api';

import { PagingConf } from '../../paging.config';
import { map, Observable } from 'rxjs';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-device-list',
  templateUrl: './device-list.component.html',
  styleUrls: ['./device-list.component.css']
})
export class DeviceListComponent extends SearchPage implements OnInit {
  maxItems$: Observable<number>;
  result$: Observable<Array<Device>>;

  constructor(public deviceService: DeviceService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.maxItems$ = this.getSearchResult((terms, _) => this.deviceService.deviceHead(1, 0, terms, undefined, 'response')).pipe(map((response) => { return (response) ? +response.headers.get('x-total-count') : 0 }));
    this.result$ = this.getSearchResult((terms, page) => this.fetchDevices(terms, page));
  }

  private fetchDevices(term: string, page: number): Observable<Array<Device>> {
    const n: number = +PagingConf.item_count;
    return this.deviceService.deviceGet(n, (page - 1) * n, term);
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
