import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, ParamMap, Router} from '@angular/router';

import {AbstractMember, Member, MemberService} from '../api';
import {NotificationsService} from 'angular2-notifications';
import {finalize, first, flatMap} from 'rxjs/operators';
import {EMPTY, of} from 'rxjs';


@Component({
  selector: 'app-member-edit',
  templateUrl: './member-create-or-edit.component.html',
  styleUrls: ['./member-create-or-edit.component.css'],
})
export class MemberCreateOrEditComponent implements OnInit, OnDestroy {

  disabled = true;
  create = false;
  memberEdit: FormGroup;
  member_id: number;

  constructor(
    public memberService: MemberService,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private router: Router,
    private notif: NotificationsService,
  ) {
    this.createForm();
  }

  createForm() {
    this.memberEdit = this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      username: ['', [Validators.required, Validators.minLength(7), Validators.maxLength(8)]],
      email: ['', [Validators.required, Validators.email]],
      roomNumber: [null, [Validators.min(1000), Validators.max(9999)]],
    });
  }

  editMember() {
    /*
    FLOW:
                +-------------+ update username  +-------------+ is allowed to +--------------------+
                |             | or create member |             |   put member  |                    |
    editMember-->  A) create  +------------------>  B) has404  +--------+------>  C) PATCH request  |
                |             |                  |             |        ^      |                    |
                +------+------+                  +-------------+        |      +--------------------+
                       |                                                |
                       +--------------------(true)----------------------+
                          regular update (does not update username)

     A) create value is transformed into an observable
        create = True means the formGroup is for creation of a member
        create = False is to update a member
     B) has404 checks that a member with that username does not exist already.
     */


    this.disabled = true;
    const v = this.memberEdit.value;

    of(this.create)
      .pipe(
        flatMap(() => {
          if (!this.create) {
            const abstractMember: AbstractMember = {
              email: v.email,
              firstName: v.firstName,
              lastName: v.lastName,
              username: v.username,
            };
            if (v.roomNumber) {
              abstractMember.room = v.roomNumber;
            }
            return this.memberService.memberMemberIdPatch(abstractMember, this.member_id, 'response');
          } else {
            const req: Member = {
              email: v.email,
              firstName: v.firstName,
              lastName: v.lastName,
              username: v.username,
              room: v.roomNumber,
              departureDate: new Date(),
            };
            return this.memberService.memberPost(req, 'response');
          }
        }),
        first(),
        finalize(() => this.disabled = false),
      )
      .subscribe((response) => {
        if (this.create) {
          this.router.navigate(['member/password', this.member_id]);
        } else {
          this.router.navigate(['member/view', this.member_id]);
        }
        this.notif.success(response.status + ': Success');
      });

  }

  memberUsernameDelete() {
    this.disabled = true;
    this.memberService.memberMemberIdDelete(this.member_id, 'response')
      .pipe(
        first(),
        finalize(() => this.disabled = false),
      )
      .subscribe((response) => {
        this.router.navigate(['member/search']);
        this.notif.success(response.status + ': Success');
      });
  }

  ngOnInit() {
    this.route.paramMap
      .pipe(
        flatMap((params: ParamMap) => {
          if (params.has('member_id')) {
            return of(params.get('member_id'));
          } else {
            // If username is not provided, we assume this is a create request
            this.disabled = false;
            this.create = true;
            return EMPTY;
          }
        }),
        flatMap((member_id) => this.memberService.memberMemberIdGet(+member_id)),
        first(),
      )
      .subscribe((member: Member) => {
        this.member_id = member.id;
        this.memberEdit.patchValue(member);
        this.disabled = false;
      });
  }

  ngOnDestroy() {
  }

}
