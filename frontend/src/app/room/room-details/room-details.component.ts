import {Component, DestroyRef, inject, OnInit} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {AsyncPipe} from "@angular/common";
import {HttpErrorResponse} from "@angular/common/http";
import {firstValueFrom, Observable} from "rxjs";
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
  MemberService,
  PortService,
  RoomService,
  AbstractRoom,
  RoomMembersService,
  SwitchService,
} from "../../api";
import {map, shareReplay} from "rxjs/operators";
import {NotificationService} from "../../notification.service";
import {ModalComponent} from "../../ui/modal.component";
import {RoomSelectComponent} from "../../ui/room-select.component";
import {ComboboxComponent, ComboboxOption} from "../../ui/combobox.component";
import {loadSwitchOptions} from "../../ui/entity-options";
import {DialogService} from "../../ui/dialog.service";

@Component({
  imports: [
    RouterModule,
    AsyncPipe,
    ReactiveFormsModule,
    ModalComponent,
    RoomSelectComponent,
    ComboboxComponent,
  ],
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
  public deleting = false;
  public ref!: number;
  public cachedMemberUsernames: Map<number, Observable<AbstractMember>> =
    new Map();
  public switchOptions: ComboboxOption[] = [];
  public switchesLoading = false;
  public switchesUnavailable = false;
  private readonly destroyRef = inject(DestroyRef);
  private readonly dialogService = inject(DialogService);
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
      roomNumberNew: [null, Validators.required],
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

  async deleteRoom(room: AbstractRoom): Promise<void> {
    const roomId = room.id;
    if (
      roomId == null ||
      !Number.isSafeInteger(roomId) ||
      roomId <= 0 ||
      this.deleting ||
      this.destroyRef.destroyed
    ) {
      return;
    }
    this.deleting = true;
    try {
      const confirmed = await this.dialogService.confirm({
        title: $localize`:@@room.delete.title:Supprimer la chambre`,
        text: $localize`:@@room.delete.confirm:Voulez-vous vraiment supprimer la chambre ${room.roomNumber}:roomNumber: ? Cette action est irréversible.`,
        confirmText: $localize`:@@common.delete:Supprimer`,
        danger: true,
      });
      if (!confirmed || this.destroyRef.destroyed) {
        return;
      }
      await firstValueFrom(
        this.roomService
          .roomIdDelete(roomId)
          .pipe(takeUntilDestroyed(this.destroyRef)),
      );
      this.notificationService.successNotification(
        $localize`:@@room.deleted:Chambre supprimée`,
      );
      void this.router.navigate(["/room/search"]);
    } catch (error) {
      if (!this.destroyRef.destroyed) {
        this.notificationService.errorNotification(
          error instanceof HttpErrorResponse ? error.status : 500,
          undefined,
          $localize`:@@room.delete.error:Impossible de supprimer la chambre.`,
        );
      }
    } finally {
      this.deleting = false;
    }
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
    if (this.roomForm.invalid) {
      return;
    }
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
              void this.router.navigate(["room", "view", room.id]);
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
    this.addPortForm.reset({switchId: null, type: "oid", value: ""});
    this.switchOptions = [];
    this.switchesLoading = true;
    this.switchesUnavailable = false;
    this.addPortOpen = true;
    loadSwitchOptions(this.switchService)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (options) => {
          this.switchOptions = options;
          this.switchesLoading = false;
          const firstId = options[0]?.value;
          this.addPortForm.controls.switchId.setValue(
            typeof firstId === "number" ? firstId : null,
          );
        },
        error: () => {
          this.switchesLoading = false;
          this.switchesUnavailable = true;
        },
      });
  }

  submitAddPort(): void {
    if (
      this.addPortForm.invalid ||
      this.switchesLoading ||
      this.switchesUnavailable
    ) {
      return;
    }
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
