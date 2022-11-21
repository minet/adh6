import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Member } from '../api';
import { MemberDeviceModule } from '../member-device/member-device.module';

@Component({
  standalone: true,
  imports: [CommonModule, MemberDeviceModule],
  selector: 'app-device',
  template: `    
    <app-member-device [member]="member"></app-member-device>
  `
})
export class DeviceComponent {
  @Input() member: Member;
  constructor() { }
}
