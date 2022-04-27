import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { AbstractMember, Member, MemberService, MembershipService, RoomService } from '../../api';
import { finalize, first, mergeMap } from 'rxjs/operators';
import { EMPTY, of } from 'rxjs';
import { NotificationService } from '../../notification.service';


@Component({
  selector: 'app-member-edit',
  templateUrl: './member-create-or-edit.component.html',
  styleUrls: ['./member-create-or-edit.component.css'],
})
export class MemberCreateOrEditComponent implements OnInit {
  disabled = true;
  create = false;
  memberEdit: FormGroup;
  member_id: number;

  constructor(
    public memberService: MemberService,
    public membershipService: MembershipService,
    public roomService: RoomService,
    private route: ActivatedRoute,
    private fb: FormBuilder,
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

    if (!this.create) {
      const abstractMember: AbstractMember = {
        email: v.email,
        firstName: v.firstName,
        lastName: v.lastName,
        username: v.username,
        roomNumber: v.roomNumber
      };
      this.memberService.memberIdPatch(abstractMember, this.member_id, 'body')
        .subscribe((_) => {
          this.router.navigate(['member/view', this.member_id]);
        });
    } else {
      const req: Member = {
        email: v.email,
        firstName: v.firstName,
        lastName: v.lastName,
        username: v.username,
        roomNumber: v.roomNumber,
        departureDate: new Date(),
      };
      this.memberService.memberPost(req, 'body')
        .subscribe((member) => {
          this.router.navigate(['/password', member.id]);
        });
    };
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
