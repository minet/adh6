import {Component, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {AbstractDevice, Device, DeviceService} from '../api';
import {PagingConf} from '../paging.config';
import {first, map} from 'rxjs/operators';
import {SearchPage} from '../search-page';

class DeviceListReponse {
  devices?: Array<Device>;
  page_number?: number;
  item_count?: number;
  item_per_page?: number;
}

@Component({
  selector: 'app-member-device-list',
  templateUrl: './member-device-list.component.html',
  styleUrls: ['./member-device-list.component.css']
})
export class MemberDeviceListComponent extends SearchPage implements OnInit {
  @Input() filter: any;
  @Input() macHighlighted: Observable<string>;
  @Input() abstractDeviceFilter: AbstractDevice = {};

  result$: Observable<DeviceListReponse>;

  private selectedDevice: string;


  toggleDeviceDetails(device: Device): void {
    if (this.isDeviceOpened(device)) {
      this.selectedDevice = null;
    } else {
      this.selectedDevice = device.mac;
    }
  }

  isDeviceOpened(device: Device): boolean {
    return this.selectedDevice === device.mac;
  }

  deviceDelete(deviceId: number) {
    this.deviceService.deviceDeviceIdDelete(deviceId)
      .pipe(
        first(),
        map(() => {
          this.updateSearch();
          return null; // @TODO return the device ?
        }),
        first(),
      )
      .subscribe(() => {
      });
  }

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
