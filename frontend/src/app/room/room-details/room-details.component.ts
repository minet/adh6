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
  SwitchService,
} from "../../api";
import {map, shareReplay, take} from "rxjs/operators";
import {NotificationService} from "../../notification.service";
import Swal from "sweetalert2";

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

  addPort(): void {
    this.switchService.switchGet(100, 0).pipe(take(1)).subscribe(switches => {
      const switchOptions = switches.reduce((acc, s) => {
        if (s.id != null) acc[s.id] = s.description ?? s.ip ?? `ID ${s.id}`;
        return acc;
      }, {} as {[key: string]: string});

      void Swal.fire({
        title: "Ajouter un port",
        icon: "info",
        html:
          '<div class="field"><label class="label">Switch</label>' +
          '<div class="select is-fullwidth"><select id="swal-port-switch">' +
          Object.entries(switchOptions).map(([id, label]) => `<option value="${id}">${label}</option>`).join('') +
          '</select></div></div>' +
          '<div class="field"><label class="label">Type d\'identifiant</label>' +
          '<div class="control"><label class="radio"><input type="radio" name="id-type" value="oid" checked> OID</label>' +
          '<label class="radio ml-2"><input type="radio" name="id-type" value="name"> Nom (Gi1/0/x)</label></div></div>' +
          '<div class="field"><label class="label">Valeur</label>' +
          '<input id="swal-port-value" class="input" type="text" placeholder="ex: 10101 ou GigabitEthernet1/0/1"></div>',
        showCancelButton: true,
        confirmButtonText: "Ajouter",
        cancelButtonText: "Annuler",
        preConfirm: () => {
          const switchId = +(document.getElementById("swal-port-switch") as HTMLSelectElement).value;
          const type = (document.querySelector('input[name="id-type"]:checked') as HTMLInputElement).value;
          const value = (document.getElementById("swal-port-value") as HTMLInputElement).value.trim();

          if (!value) {
            Swal.showValidationMessage("La valeur est requise");
            return false;
          }
          return {switchId, type, value};
        }
      }).then(result => {
        if (!result.isConfirmed || !result.value) return;
        const {switchId, type, value} = result.value;
        
        const port: AbstractPort = {
          switchObj: switchId,
          room: this.room_id,
          oid: type === 'oid' ? value : value, // If we had discover, we'd find OID from name here
          portNumber: type === 'name' ? value : `Port ${value}`
        };

        this.portService.portPost(port).subscribe({
          next: () => {
            this.notificationService.successNotification("Port ajouté");
            this.refreshInfo();
          },
          error: (err: {status: number}) => this.notificationService.errorNotification(err.status)
        });
      });
    });
  }
}
