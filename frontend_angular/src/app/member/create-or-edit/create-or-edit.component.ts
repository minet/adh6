import { Component, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { AbstractRoom, Member, MemberBody, MemberService, MembershipService, RoomMembersService, RoomService } from '../../api';
import { finalize, first, mergeMap } from 'rxjs/operators';
import { EMPTY, of } from 'rxjs';
import { NotificationService } from '../../notification.service';


@Component({
  selector: 'app-create-edit',
  templateUrl: './create-or-edit.component.html',
  styleUrls: ['./create-or-edit.component.css'],
})
export class CreateOrEditComponent implements OnInit {
  disabled = true;
  create = false;
  memberEdit: UntypedFormGroup;
  member_id: number;

  constructor(
    public memberService: MemberService,
    public membershipService: MembershipService,
    public roomService: RoomService,
    public roomMemberService: RoomMembersService,
    private route: ActivatedRoute,
    private fb: UntypedFormBuilder,
    private router: Router,
    private notificationService: NotificationService,
  ) {
    this.createForm();
  }

  createForm() {
    this.memberEdit = this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      username: ['', [Validators.required, Validators.minLength(7), Validators.maxLength(255)]],
      email: ['', [Validators.required, Validators.email]],
      roomNumber: [null, [Validators.min(0), Validators.max(9999)]],
    });
  }

  editMember() {
    this.disabled = true;
    const v = this.memberEdit.value;

    const body: MemberBody = {
      mail: v.email,
      firstName: v.firstName,
      lastName: v.lastName,
      username: v.username,
    };
    this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{ roomNumber: v.roomNumber })
      .subscribe(rooms => {
        if (rooms.length === 0) {
          this.notificationService.errorNotification(404, "Chambre (" + v.roomNumber + ")");
          return
        }
        const room = rooms[0];
        if (!this.create) {
          this.memberService.memberIdPatch(this.member_id, body)
            .subscribe(() => {
              this.roomMemberService.roomIdMemberAddPatch(room.id, { id: this.member_id }).subscribe(() => this.router.navigate(['member/view', this.member_id]))
            });
        } else {
          this.memberService.memberPost(body, 'body')
            .subscribe((id) => {
              this.roomMemberService.roomIdMemberAddPatch(room.id, { id: id }).subscribe(() => this.router.navigate(['/password', id, 1]))
            });
        };
      });
  }

  memberUsernameDelete() {
    this.disabled = true;
    this.memberService.memberIdDelete(this.member_id, 'response')
      .pipe(
        first(),
        finalize(() => this.disabled = false),
      )
      .subscribe((_) => {
        this.router.navigate(['member/search']);
        this.notificationService.successNotification();
      });
  }

  ngOnInit() {
    this.route.paramMap
      .pipe(
        mergeMap((params: ParamMap) => {
          if (params.has('member_id')) {
            return of(params.get('member_id'));
          } else {
            // If username is not provided, we assume this is a create request
            this.disabled = false;
            this.create = true;
            return EMPTY;
          }
        }),
        mergeMap((member_id) => this.memberService.memberIdGet(+member_id)),
        first(),
      )
      .subscribe((member: Member) => {
        this.member_id = member.id;
        this.memberEdit.patchValue(member);
        this.disabled = false;
      });
  }
}
