import { CommonModule } from '@angular/common';
import { HttpEvent } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Observable, switchMap, timer } from 'rxjs';
import { MemberService } from '../../../api';
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
  public log$: Observable<Array<string> | HttpEvent<string[]>>;

  public showLogs = false;
  public member$ = this.memberDetailService.member$;
  private content: string;  // for log formatting

  constructor(
    private memberService: MemberService,
    private memberDetailService: MemberDetailService
  ) { }

  ngOnInit(): void {
    this.refreshLog();
  }

  refreshLog(): void {
    this.log$ = timer(0, 10 * 1000)
      .pipe(switchMap(
        () => this.member$
          .pipe(switchMap((member) => this.memberService.memberIdLogsGet(member.id, this.getDhcp, 'body')))
      ));
  }

  extractMsgFromLog(log: string): string {
    this.content = ' ' + log.substr(log.indexOf(' ') + 1);

    if (this.content.includes('Login OK')) {
      return this.content.replace(new RegExp('Login OK:', 'gi'), match => {
        return '<font color="green">'.concat(match).concat('</font>');
      });
    } else if (this.content.includes('Login incorrect')) {
      return this.content.replace(new RegExp('Login incorrect', 'gi'), match => {
        return '<font color="red">'.concat(match).concat('</font>');
      });
    } else {
      return this.content;
    }
  }
}
