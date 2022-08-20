import { Component, Input } from '@angular/core';
import { map, Observable, shareReplay } from 'rxjs';
import { AbstractDevice, DeviceFilter, DeviceService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-member-device-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent extends SearchPage<number> {
  @Input() abstractDeviceFilter: AbstractDevice = {};

  public cachedDevices: Map<Number, Observable<AbstractDevice>> = new Map();
  constructor(public deviceService: DeviceService) {
    super((terms, page) => this.deviceService.deviceGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, <DeviceFilter>{
      terms: terms,
      member: this.abstractDeviceFilter.member,
      connectionType: this.abstractDeviceFilter.connectionType
    }, 'response').pipe(
      map(response => {
        for (let i of response.body) {
          this.cachedDevices.set(+i, this.deviceService.deviceIdGet(i)
            .pipe(
              shareReplay(1)
            )
          );
        }
        return response
      })
    )
    );
  }

  updateSearch() {
    this.getSearchResult();
  }

  public getDevice(id: number) {
    return this.cachedDevices.get(id)
  }
}
