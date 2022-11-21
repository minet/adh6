import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { MemberService, AbstractMember } from '../../api';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { map, switchMap } from 'rxjs/operators';
import { CommonModule } from '@angular/common';
import { MemberDetailService } from './member-detail.service';
import { Toast } from '../../notification.service';

@Component({
  standalone: true,
  imports: [CommonModule, RouterModule],
  selector: 'app-view',
  templateUrl: './view.component.html'
})

export class ViewComponent implements OnInit {
  public currentTab = "profile";
  public member$: Observable<AbstractMember>;

  constructor(
    public memberService: MemberService,
    private route: ActivatedRoute,
    private memberDetailService: MemberDetailService
  ) { }

  ngOnInit() {
    this.refreshInfo();
    this.memberDetailService.updateMemberInfos.subscribe(msg => {
      this.refreshInfo();
      Toast.fire("Adhérent mis à jour", msg);
    })
  }

  refreshInfo(): void {
    this.member$ = this.route.params
      .pipe(
        switchMap(params => this.memberService.memberIdGet(params['member_id'])),
        map(member => {
          this.memberDetailService.refreshMember(member);
          return member;
        })
      )
  }
}
