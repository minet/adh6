import {Component, OnInit} from "@angular/core";
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {ActivatedRoute, ParamMap, Router} from "@angular/router";

import {
  MemberBody,
  MemberService,
  RoomMembersService,
  RoomService,
} from "../../api";
import {mergeMap} from "rxjs/operators";
import {EMPTY, of, switchMap, catchError} from "rxjs";
import {Toast} from "../../notification.service";

interface MemberEditForm {
  firstName: FormControl<string>;
  lastName: FormControl<string>;
  username: FormControl<string>;
  email: FormControl<string>;
  roomNumber: FormControl<number | null>;
}

@Component({
  imports: [ReactiveFormsModule, FormsModule],
  selector: "app-create-edit",
  templateUrl: "./create-or-edit.component.html",
})
export class CreateOrEditComponent implements OnInit {
  create = false;
  public memberEdit: FormGroup<MemberEditForm>;
  private member_id!: number;

  constructor(
    public memberService: MemberService,
    public roomService: RoomService,
    public roomMemberService: RoomMembersService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
  ) {
    this.memberEdit = new FormGroup<MemberEditForm>({
      firstName: new FormControl("", {
        nonNullable: true,
        validators: [Validators.required.bind(Validators)],
      }),
      lastName: new FormControl("", {
        nonNullable: true,
        validators: [Validators.required.bind(Validators)],
      }),
      username: new FormControl("", {
        nonNullable: true,
        validators: [
          Validators.required,
          Validators.minLength(7),
          Validators.maxLength(255),
        ],
      }),
      email: new FormControl("", {
        nonNullable: true,
        validators: [Validators.required, Validators.email],
      }),
      roomNumber: new FormControl<number | null>(null),
    });
  }

  editMember() {
    const v = this.memberEdit.value;
    const body: MemberBody = {
      mail: v.email!,
      firstName: v.firstName!,
      lastName: v.lastName!,
      username: v.username!,
    };

    const roomFilter =
      v.roomNumber != null ? {roomNumber: v.roomNumber} : undefined;

    this.roomService.roomGet(1, 0, undefined, roomFilter).subscribe((rooms) => {
      if (!this.create) {
        this.memberService.memberIdPatch(this.member_id, body).subscribe(() => {
          if (rooms.length > 0 && rooms[0].id != null) {
            this.roomMemberService
              .roomIdMemberPost(rooms[0].id, {id: this.member_id})
              .subscribe(
                () =>
                  void this.router.navigate(["member/view", this.member_id]),
              );
          } else {
            void this.router.navigate(["member/view", this.member_id]);
          }
        });
      } else {
        this.memberService.memberPost(body).subscribe((id) => {
          if (rooms.length > 0 && rooms[0].id != null && id != null) {
            this.roomMemberService
              .roomIdMemberPost(rooms[0].id, {id: id})
              .subscribe(() => void this.router.navigate(["/password", id, 1]));
          } else {
            void this.router.navigate(["/password", id, 1]);
          }
        });
      }
    });
  }

  delete(): void {
    this.memberService.memberIdDelete(this.member_id).subscribe((_) => {
      void this.router.navigate(["member/search"]);
      void Toast.fire("User suprimé", "", "success");
    });
  }

  ngOnInit() {
    this.route.paramMap
      .pipe(
        mergeMap((params: ParamMap) => {
          if (params.has("member_id")) {
            const memberId = params.get("member_id");
            if (memberId) {
              return of(memberId);
            }
          }
          // If username is not provided, we assume this is a create request
          this.create = true;
          return EMPTY;
        }),
        mergeMap((member_id) => {
          if (member_id) {
            return this.memberService.memberIdGet(+member_id);
          }
          return EMPTY;
        }),
        mergeMap((member) => {
          if (member.id != null) {
            this.member_id = member.id;
            this.memberEdit.patchValue(member);
            return this.roomMemberService.roomMemberIdGet(member.id).pipe(
              switchMap((roomId) => this.roomService.roomIdGet(roomId)),
              catchError(() => EMPTY),
            );
          }
          return EMPTY;
        }),
      )
      .subscribe((room) => {
        if (room.roomNumber != null) {
          this.memberEdit.patchValue({roomNumber: room.roomNumber});
        }
      });
  }
}
