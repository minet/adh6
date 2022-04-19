import { Component, OnInit } from '@angular/core';
import { Device, DeviceService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-device-list',
  templateUrl: './device-list.component.html',
  styleUrls: ['./device-list.component.css']
})
export class DeviceListComponent extends SearchPage<Device> implements OnInit {
  constructor(public deviceService: DeviceService) {
    super((terms, page) => this.deviceService.deviceGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, "response"));
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
