import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { AbstractMember, Member, MemberBody, MemberService, RoomMembersService } from '../../api';
import { map, switchMap } from 'rxjs/operators';
import { Observable, of } from 'rxjs';
import { Toast } from '../../notification.service';
import { CommonModule } from '@angular/common';
import { FormComponent } from './form/form.component';

@Component({
  standalone: true,
  imports: [CommonModule, FormComponent],
  selector: 'app-create-edit',
  templateUrl: './create-or-edit.component.html'
})
export class CreateOrEditComponent implements OnInit {
  public member$: Observable<AbstractMember>;

  constructor(
    private memberService: MemberService,
    private roomMemberService: RoomMembersService,
    private route: ActivatedRoute,
    private router: Router
  ) { }

  editMember(newMember: {member: MemberBody, room: number}, member?: Member) {
    if (member.username) {
      this.memberService.memberIdPatch(member.id, newMember.member)
        .pipe(map(() => this.roomMemberService.roomRoomNumberMemberPost(newMember.room, { login: newMember.member.username })))
        .subscribe(() => this.router.navigate(['member/view', member.id]))
    } else {
      this.memberService.memberPost(newMember.member)
        .subscribe((id) => {
          this.roomMemberService.roomRoomNumberMemberPost(newMember.room, { login: newMember.member.username }).subscribe(() => this.router.navigate(['/password', id, 1]))
        });
    };
  }

  delete(member: Member) {
    this.memberService.memberIdDelete(member.id)
      .subscribe(() => {
        this.router.navigate(['member/search']);
        Toast.fire("User suprimé", "", 'success')
      });
  }

  ngOnInit() {
    this.member$ = this.route.paramMap.pipe(switchMap((params: ParamMap) => params.has('member_id') ? this.memberService.memberIdGet(+params.get('member_id')) : of(<AbstractMember>{})))
  }
}
