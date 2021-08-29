import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, ParamMap, Router} from '@angular/router';

import {AbstractMember, AbstractMembership, AbstractRoom, Member, MemberService, MembershipService, RoomService} from '../api';
import {NotificationsService} from 'angular2-notifications';
import {finalize, first, mergeMap} from 'rxjs/operators';
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
    public membershipService: MembershipService,
    public roomService: RoomService,
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
      roomNumber: [null, [Validators.min(0), Validators.max(9999)]],
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

    this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{roomNumber:v.roomNumber})
      .subscribe((rooms) => {
        if (rooms.length == 0) {
          this.notif.alert('Room not Found', "Room "+v.roomNumber+" has not be found")
          return undefined
        }
        if (!this.create) {
          const abstractMember: AbstractMember = {
            email: v.email,
            firstName: v.firstName,
            lastName: v.lastName,
            username: v.username,
            room: rooms[0].id
          };
          this.memberService.memberMemberIdPatch(abstractMember, this.member_id, 'body')
            .subscribe((_) => {
              this.router.navigate(['member/view', this.member_id]);
            });
        } else {
          const req: Member = {
            email: v.email,
            firstName: v.firstName,
            lastName: v.lastName,
            username: v.username,
            room: rooms[0].id,
            departureDate: new Date(),
          };
          this.memberService.memberPost(req, 'body')
            .subscribe((member) => {
              this.router.navigate(['member/password', member.id]);
            });
        }
      })

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
        mergeMap((member_id) => this.memberService.memberMemberIdGet(+member_id)),
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
