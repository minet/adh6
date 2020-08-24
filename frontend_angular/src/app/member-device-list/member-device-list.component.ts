import {Component, EventEmitter, Input, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {Device, DeviceService} from '../api';

@Component({
  selector: 'app-member-device-list',
  templateUrl: './member-device-list.component.html',
  styleUrls: ['./member-device-list.component.css']
})
export class MemberDeviceListComponent implements OnInit {
  @Input() devices: Observable<Device[]>;
  @Input() filter: any;
  @Input() macHighlighted: Observable<string>;

  @Input() deviceDelete: Function;

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

  constructor(public deviceService: DeviceService) {
  }

  ngOnInit() {
  }

}
