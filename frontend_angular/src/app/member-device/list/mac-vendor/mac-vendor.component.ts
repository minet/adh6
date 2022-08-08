import { Component, Input, OnInit } from '@angular/core';
import { DeviceService } from '../../../api';
import { first, map } from 'rxjs/operators';

@Component({
  selector: 'app-mac-vendor',
  templateUrl: './mac-vendor.component.html',
  styleUrls: ['./mac-vendor.component.css']
})
export class MacVendorComponent implements OnInit {

  @Input() device_id: number;
  vendor = '';

  constructor(
    public deviceService: DeviceService
  ) { }

  ngOnInit() {
    this.deviceService.deviceIdVendorGet(this.device_id, 'body')
      .pipe(
        map((data) => data),
        first(),
      )
      .subscribe((vendor) => {
        this.vendor = vendor;
      });
  }
}
