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
import {map, mergeMap} from "rxjs/operators";
import {EMPTY, of, switchMap, catchError} from "rxjs";
import {NotificationService} from "../../notification.service";
import {RoomSelectComponent} from "../../ui/room-select.component";
import {detailOf} from "../../shared/http-error";

interface MemberEditForm {
  firstName: FormControl<string>;
  lastName: FormControl<string>;
  username: FormControl<string>;
  email: FormControl<string>;
  roomNumber: FormControl<number | null>;
  permanent: FormControl<boolean>;
  wifiOnly: FormControl<boolean>;
  preferredLanguage: FormControl<MemberBody.PreferredLanguageEnum>;
}

@Component({
  imports: [ReactiveFormsModule, FormsModule, RoomSelectComponent],
  selector: "app-create-edit",
  templateUrl: "./create-or-edit.component.html",
})
export class CreateOrEditComponent implements OnInit {
  create = false;
  loading = false;
  submitError: string | null = null;
  public memberEdit: FormGroup<MemberEditForm>;
  private member_id!: number;

  constructor(
    public memberService: MemberService,
    public roomService: RoomService,
    public roomMemberService: RoomMembersService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
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
      permanent: new FormControl<boolean>(false, {nonNullable: true}),
      wifiOnly: new FormControl<boolean>(false, {nonNullable: true}),
      preferredLanguage: new FormControl<MemberBody.PreferredLanguageEnum>(
        "fr",
        {
          nonNullable: true,
        },
      ),
    });
  }

  editMember() {
    if (this.memberEdit.invalid || this.loading) {
      return;
    }
    this.loading = true;
    this.submitError = null;
    const v = this.memberEdit.value;
    const permanent = this.create ? false : v.permanent;
    const wifiOnly = this.create ? false : v.wifiOnly;
    const body: MemberBody = {
      mail: v.email!,
      firstName: v.firstName!,
      lastName: v.lastName!,
      username: v.username!,
      permanent,
      wifiOnly,
      preferredLanguage: v.preferredLanguage,
    };

    const roomFilter =
      !wifiOnly && v.roomNumber != null
        ? {roomNumber: v.roomNumber}
        : undefined;

    const rooms$ =
      roomFilter == null
        ? of([])
        : this.roomService.roomGet(1, 0, undefined, roomFilter);

    rooms$.subscribe({
      next: (rooms) => {
        if (roomFilter != null && rooms.length === 0) {
          this.loading = false;
          this.memberEdit.controls.roomNumber.setErrors({roomNotFound: true});
          return;
        }
        const roomId = !wifiOnly && rooms.length > 0 ? rooms[0].id : undefined;
        const save$ = this.create
          ? this.memberService.memberPost(body)
          : this.memberService
              .memberIdPatch(this.member_id, body)
              .pipe(map(() => this.member_id));
        save$.subscribe({
          next: (id) => this.assignRoomThenLeave(id, roomId),
          error: (error: unknown) => this.onSubmitError(error),
        });
      },
      error: (error: unknown) => this.onSubmitError(error),
    });
  }

  private assignRoomThenLeave(id: number, roomId: number | undefined) {
    const leave = () =>
      void this.router.navigate(
        this.create ? ["/password", id, 1] : ["member/view", id, "profile"],
      );
    if (roomId == null) {
      leave();
      return;
    }
    this.roomMemberService
      .roomIdMemberPost(roomId, {id})
      .subscribe({next: leave, error: leave});
  }

  private onSubmitError(error: unknown) {
    this.loading = false;
    const status = (error as {status?: number})?.status;
    const detail = detailOf(error, "");
    if (status === 400 && detail.endsWith("already exists")) {
      this.memberEdit.controls.username.setErrors({taken: true});
      return;
    }
    this.submitError =
      detail ||
      $localize`:@@member.form.submit.error:Erreur lors de l'enregistrement du membre.`;
  }

  delete(): void {
    this.memberService.memberIdDelete(this.member_id).subscribe((_) => {
      void this.router.navigate(["member/search"]);
      this.notificationService.successNotification(
        $localize`:@@member.deleted:Adhérent supprimé`,
      );
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
