import { Component, Input, OnInit } from '@angular/core';
import { map, Observable, shareReplay } from 'rxjs';
import { AbstractDevice, DeviceService, Member } from '../../api';

@Component({
  selector: 'app-member-device-list',
  templateUrl: './list.component.html'
})
export class MemberDeviceListComponent implements OnInit {
  @Input() deviceType: string;
  @Input() member: Member;

  public deviceIds$: Observable<number[]>;
  private cachedDevices: Map<Number, Observable<AbstractDevice>> = new Map();
  
  constructor(private deviceService: DeviceService) { }

  ngOnInit(): void {
    this.updateSearch();
  }

  updateSearch() {
    this.deviceIds$ = this.deviceService.deviceMemberLoginGet(this.member.username, (this.deviceType == "wireless") ? this.deviceType : "wired").pipe(
      map(deviceIds => {
        deviceIds.forEach(i => this.cachedDevices.set(+i, this.deviceService.deviceIdGet(i).pipe(shareReplay(1))));
        return deviceIds;
      })
    )
  }

  public getDevice(id: number) {
    return this.cachedDevices.get(id)
  }
}
