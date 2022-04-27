import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { AbstractDevice, Device, DeviceService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-member-device-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent extends SearchPage<Device> implements OnInit {
  @Input() filter: any;
  @Input() macHighlighted: Observable<string>;
  @Input() abstractDeviceFilter: AbstractDevice = {};
  constructor(public deviceService: DeviceService) {
    super((terms, page) => this.deviceService.deviceGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, this.abstractDeviceFilter, 'response'));
  }

  ngOnInit() {
    super.ngOnInit();
  }
}
