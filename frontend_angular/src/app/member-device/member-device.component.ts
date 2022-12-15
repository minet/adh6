import { Component, Input, ViewChild } from '@angular/core';
import { AbstractDevice, Member } from '../api';
import { MemberDeviceListComponent } from './list/list.component';

@Component({
  selector: 'app-member-device',
  templateUrl: './member-device.component.html'
})
export class MemberDeviceComponent {
  @Input() member: Member;

  @ViewChild(MemberDeviceListComponent) wiredList: MemberDeviceListComponent;
  @ViewChild(MemberDeviceListComponent) wirelessList: MemberDeviceListComponent;

  constructor() {}
}
