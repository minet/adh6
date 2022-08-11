import { Component, Input, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { Member, MemberService, MemberStatus } from '../api';

@Component({
  selector: 'app-auto-troubleshoot',
  templateUrl: './auto-troubleshoot.component.html',
  styleUrls: ['./auto-troubleshoot.component.sass']
})
export class AutoTroubleshootComponent implements OnInit {
  statuses$: Observable<MemberStatus[]>;

  @Input() member: Member;

  constructor(private memberService: MemberService) { }

  ngOnInit(): void {
    this.statuses$ = this.memberService.memberIdStatusesGet(this.member.id, 'body');
  }

}
