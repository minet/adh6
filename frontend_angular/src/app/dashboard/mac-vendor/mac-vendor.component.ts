import {Component, Input, OnDestroy, OnInit} from '@angular/core';
import {DeviceService} from '../../api';
import {first, map} from 'rxjs/operators';

@Component({
  selector: 'app-mac-vendor',
  templateUrl: './mac-vendor.component.html',
  styleUrls: ['./mac-vendor.component.css']
})
export class MacVendorComponent implements OnInit, OnDestroy {

  @Input() device_id: number;
  vendor = '';
  private alive = true;

  constructor(
    public deviceService: DeviceService
  ) {
  }

  ngOnInit() {
    this.deviceService.vendorGet(this.device_id, 'body', false, false)
      .pipe(
        map((data) => data.vendorname),
        first(),
      )
      .subscribe((vendor) => {
        this.vendor = vendor;
      });
  }

  ngOnDestroy() {
    this.alive = false;
  }

}
