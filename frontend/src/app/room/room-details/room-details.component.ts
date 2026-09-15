import {Component, OnInit} from "@angular/core";
import {AsyncPipe} from "@angular/common";
import {Observable} from "rxjs";
import {
  FormControl,
  FormGroup,
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import {ActivatedRoute, Router, RouterModule} from "@angular/router";
import {
  AbstractMember,
  AbstractPort,
  AbstractSwitch,
  MemberService,
  PortService,
  RoomService,
  AbstractRoom,
  RoomMembersService,
  SwitchService,
} from "../../api";
import {map, shareReplay, take} from "rxjs/operators";
import {NotificationService} from "../../notification.service";
import {ModalComponent} from "../../ui/modal.component";

@Component({
  imports: [RouterModule, AsyncPipe, ReactiveFormsModule, ModalComponent],
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
  public switches: AbstractSwitch[] = [];
  public addPortOpen = false;
  public addPortForm = new FormGroup({
    switchId: new FormControl<number | null>(null, Validators.required),
    type: new FormControl<"oid" | "name">("oid", {nonNullable: true}),
    value: new FormControl("", {
      nonNullable: true,
      validators: [Validators.required],
    }),
  });

  constructor(
    private readonly notificationService: NotificationService,
    private readonly router: Router,
    public roomMemberService: RoomMembersService,
    public roomService: RoomService,
    public portService: PortService,
    public memberService: MemberService,
    public switchService: SwitchService,
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
    this.ports$ = this.portService.portGet(undefined, undefined, undefined, {
      room: this.room_id,
    });
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
      .roomGet(1, 0, undefined, {roomNumber: v.roomNumberNew})
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

  addPort(): void {
    this.switchService
      .switchGet(100, 0)
      .pipe(take(1))
      .subscribe((switches) => {
        this.switches = switches.filter((s) => s.id != null);
        this.addPortForm.reset({
          switchId: this.switches[0]?.id ?? null,
          type: "oid",
          value: "",
        });
        this.addPortOpen = true;
      });
  }

  submitAddPort(): void {
    const {switchId, type, value} = this.addPortForm.getRawValue();
    const trimmed = value.trim();
    if (switchId == null || !trimmed) {
      return;
    }
    this.addPortOpen = false;

    const port: AbstractPort = {
      switchObj: switchId,
      room: this.room_id,
      // Without discovery the OID can't be resolved from a name
      oid: trimmed,
      portNumber: type === "name" ? trimmed : `Port ${trimmed}`,
    };

    this.portService.portPost(port).subscribe({
      next: () => {
        this.notificationService.successNotification(
          $localize`:@@room.details.port-added:Port ajouté`,
        );
        this.refreshInfo();
      },
      error: (err: {status: number}) =>
        this.notificationService.errorNotification(err.status),
    });
  }
}
