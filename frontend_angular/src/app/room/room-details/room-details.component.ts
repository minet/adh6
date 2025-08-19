import {Component, OnInit} from "@angular/core";
import {AsyncPipe} from "@angular/common";
import {Observable} from "rxjs";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import {ActivatedRoute, Router, RouterModule} from "@angular/router";
import {
  AbstractMember,
  AbstractPort,
  MemberService,
  PortService,
  RoomService,
  AbstractRoom,
  RoomMembersService,
} from "../../api";
import {map, shareReplay} from "rxjs/operators";
import {NotificationService} from "../../notification.service";

@Component({
  imports: [RouterModule, AsyncPipe, ReactiveFormsModule],
  selector: "app-room-details",
  templateUrl: "./room-details.component.html",
})
export class RoomDetailsComponent implements OnInit {
  public room$!: Observable<AbstractRoom>;
  public ports$!: Observable<AbstractPort[]>;
  public memberIds$!: Observable<number[]>;
  private room_id!: number;
  public roomForm!: UntypedFormGroup;
  public EmmenagerForm!: UntypedFormGroup;
  public isDemenager = false;
  public enabled = false;
  public ref!: number;
  public cachedMemberUsernames: Map<number, Observable<AbstractMember>> =
    new Map();

  constructor(
    private readonly notificationService: NotificationService,
    private readonly router: Router,
    public roomMemberService: RoomMembersService,
    public roomService: RoomService,
    public portService: PortService,
    public memberService: MemberService,
    private readonly fb: UntypedFormBuilder,
    private readonly route: ActivatedRoute,
  ) {
    this.createForm();
  }

  createForm() {
    this.ngOnInit();
    this.roomForm = this.fb.group({
      roomNumberNew: [
        "",
        [Validators.min(-1), Validators.max(9999), Validators.required],
      ],
    });
    this.EmmenagerForm = this.fb.group({
      username: [
        "",
        [
          Validators.minLength(6),
          Validators.maxLength(20),
          Validators.required,
        ],
      ],
    });
  }

  onDemenager(memberId: number) {
    this.ref = memberId;
    this.isDemenager = !this.isDemenager;
  }

  refreshInfo() {
    this.room$ = this.roomService.roomIdGet(this.room_id).pipe(
      map((room) => {
        this.memberIds$ = this.roomMemberService
          .roomIdMemberGet(this.room_id)
          .pipe(
            map((response) => {
              for (const i of response) {
                this.cachedMemberUsernames.set(
                  +i,
                  this.memberService.memberIdGet(+i).pipe(shareReplay(1)),
                );
              }
              return response;
            }),
          );
        return room;
      }),
    );
    this.ports$ = this.portService.portGet(undefined, undefined, undefined, <
      AbstractPort
    >{room: this.room_id});
  }

  onSubmitComeInRoom() {
    const v = this.EmmenagerForm.value;
    this.memberService.memberGet(1, 0, v.username).subscribe(
      (member_list) => {
        const member = member_list[0];
        this.roomMemberService
          .roomIdMemberPost(this.room_id, {id: member})
          .subscribe(() => {
            this.refreshInfo();
            this.notificationService.successNotification();
          });
      },
      () => {
        this.notificationService.errorNotification(
          404,
          undefined,
          "Member " + v.username + " does not exists",
        );
      },
    );
  }

  onSubmitMoveRoom(memberId: number) {
    const v = this.roomForm.value;

    this.roomService
      .roomGet(1, 0, undefined, <AbstractRoom>{roomNumber: v.roomNumberNew})
      .subscribe((rooms) => {
        if (rooms.length == 0) {
          this.notificationService.errorNotification(
            404,
            undefined,
            "The room with number: " + v.roomNumberNew + " does not exists",
          );
          return;
        }
        const room = rooms[0];
        if (room.id != null) {
          this.roomMemberService
            .roomIdMemberPost(room.id, {id: memberId})
            .subscribe(() => {
              this.refreshInfo();
              this.onDemenager(memberId);
              void this.router.navigate(["room", "view", v.roomNumberNew]);
              this.notificationService.successNotification();
            });
        } else {
          this.notificationService.errorNotification(
            400,
            undefined,
            "Invalid room ID",
          );
        }
      });
  }

  onRemoveFromRoom(memberId: number) {
    this.roomMemberService
      .roomIdMemberDelete(this.room_id, memberId)
      .subscribe(() => {
        this.refreshInfo();
        this.notificationService.successNotification();
      });
  }

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.room_id = +params["room_id"];
      this.refreshInfo();
    });
  }

  public getMemberUsername(id: number) {
    return this.cachedMemberUsernames.get(id);
  }
}
