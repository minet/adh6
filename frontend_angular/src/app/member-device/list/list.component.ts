import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {AbstractDevice, Device, DeviceService} from '../../api';
import {PagingConf} from '../../paging.config';
import {first, map} from 'rxjs/operators';
import {SearchPage} from '../../search-page';

class DeviceListReponse {
  devices?: Array<Device>;
  page_number?: number;
  item_count?: number;
  item_per_page?: number;
}

@Component({
  selector: 'app-member-device-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent extends SearchPage implements OnInit {
  @Input() filter: any;
  @Input() macHighlighted: Observable<string>;
  @Input() abstractDeviceFilter: AbstractDevice = {};

  result$: Observable<DeviceListReponse>;

  constructor(public deviceService: DeviceService) {
    super();
  }

  ngOnInit() {
    this.updateSearch();
  }

  updateSearch() {
    this.result$ = this.getSearchResult((terms, page) => this.fetchDevices(terms, page));
  }

  private fetchDevices(terms: string, page: number) {
    const n = +PagingConf.item_count;

    return this.deviceService.deviceGet(n, (page - 1) * n, terms, this.abstractDeviceFilter, 'response')
      .pipe(
        // switch to new search observable each time the term changes
        map((response) => <DeviceListReponse>{
          devices: response.body,
          item_count: +response.headers.get('x-total-count'),
          page_number: page,
          item_per_page: n,
        }),
      );
  }

}
