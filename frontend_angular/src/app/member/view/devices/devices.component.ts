import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Observable, switchMap, timer } from 'rxjs';
import { DeviceService } from '../../../api';
import { MemberDeviceModule } from '../../../member-device/member-device.module';
import { MemberDetailService } from '../member-detail.service';

@Component({
  standalone: true,
  imports: [CommonModule, MemberDeviceModule],
  selector: 'app-devices',
  templateUrl: './devices.component.html'
})
export class DevicesComponent implements OnInit {
  public getDhcp = false;
  public showLogs = false;
  public log$: Observable<Array<string>>;

  constructor(
    private deviceService: DeviceService,
    public memberDetailService: MemberDetailService
  ) { }

  ngOnInit(): void {
    this.log$ = timer(0, 10 * 1000)
      .pipe(
        switchMap(() => this.memberDetailService.member$),
        switchMap((member) => this.deviceService.deviceMemberLoginLogsGet(member.username, this.getDhcp))
      );
  }

  extractMsgFromLog(log: string): string {
    let content = ' ' + log.substr(log.indexOf(' ') + 1);
    if (content.includes('Login OK')) {
      content.replace(new RegExp('Login OK:', 'gi'), match => {
        return '<font color="green">'.concat(match).concat('</font>');
      });
    } else if (content.includes('Login incorrect')) {
      content.replace(new RegExp('Login incorrect', 'gi'), match => {
        return '<font color="red">'.concat(match).concat('</font>');
      });
    }
    return content;
  }
}
