import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { MemberBody, MemberService, RoomMembersService, RoomService } from '../../api';
import { mergeMap } from 'rxjs/operators';
import { EMPTY, of } from 'rxjs';
import { Toast } from '../../notification.service';
import { CommonModule } from '@angular/common';

interface MemberEditForm {
  firstName: FormControl<string>;
  lastName: FormControl<string>;
  username: FormControl<string>;
  email: FormControl<string>;
  roomNumber: FormControl<number>;
}

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  selector: 'app-create-edit',
  templateUrl: './create-or-edit.component.html'
})
export class CreateOrEditComponent implements OnInit {
  create = false;
  public memberEdit: FormGroup<MemberEditForm>;
  private member_id: number;

  constructor(
    public memberService: MemberService,
    public roomService: RoomService,
    public roomMemberService: RoomMembersService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.memberEdit = new FormGroup<MemberEditForm>({
      firstName: new FormControl('', [Validators.required]),
      lastName: new FormControl('', Validators.required),
      username: new FormControl('', [Validators.required, Validators.minLength(7), Validators.maxLength(255)]),
      email: new FormControl('', [Validators.required, Validators.email]),
      roomNumber: new FormControl(null),
    });
  }

  editMember() {
    const v = this.memberEdit.value;
    const body: MemberBody = {
      mail: v.email,
      firstName: v.firstName,
      lastName: v.lastName,
      username: v.username,
    };
    this.roomService.roomGet(1, 0, undefined, { roomNumber: v.roomNumber })
      .subscribe(rooms => {
        if (!this.create) {
          this.memberService.memberIdPatch(this.member_id, body)
            .subscribe(() => {
              this.roomMemberService.roomIdMemberPost(rooms[0].id, { id: this.member_id }).subscribe(() => this.router.navigate(['member/view', this.member_id]))
            });
        } else {
          this.memberService.memberPost(body)
            .subscribe((id) => {
              this.roomMemberService.roomIdMemberPost(rooms[0].id, { id: id }).subscribe(() => this.router.navigate(['/password', id, 1]))
            });
        };
      });
  }

  delete() {
    this.memberService.memberIdDelete(this.member_id)
      .subscribe((_) => {
        this.router.navigate(['member/search']);
        Toast.fire("User suprimé", "", 'success')
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
            this.create = true;
            return EMPTY;
          }
        }),
        mergeMap((member_id) => this.memberService.memberIdGet(+member_id)),
      )
      .subscribe((member) => {
        this.member_id = member.id;
        this.memberEdit.patchValue(member);
      });
  }
}
