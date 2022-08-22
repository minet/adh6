import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AbstractMember, AbstractPort, MemberService, PortService, RoomService, AbstractRoom, RoomMembersService } from '../../api';
import { map, shareReplay } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-room-details',
  templateUrl: './room-details.component.html'
})
export class RoomDetailsComponent implements OnInit {
  public room$: Observable<AbstractRoom>;
  public ports$: Observable<Array<AbstractPort>>;
  public memberIds$: Observable<Array<number>>;
  private room_id: number;
  public roomForm: UntypedFormGroup;
  public EmmenagerForm: UntypedFormGroup;
  public isDemenager = false;
  public ref: number;
  public cachedMemberUsernames: Map<Number, Observable<AbstractMember>> = new Map();

  constructor(
    private notificationService: NotificationService,
    private router: Router,
    public roomMemberService: RoomMembersService,
    public roomService: RoomService,
    public portService: PortService,
    public memberService: MemberService,
    private fb: UntypedFormBuilder,
    private route: ActivatedRoute,
  ) {
    this.createForm();
  }

  createForm() {
    this.ngOnInit();
    this.roomForm = this.fb.group({
      roomNumberNew: ['', [Validators.min(-1), Validators.max(9999), Validators.required]],
    });
    this.EmmenagerForm = this.fb.group({
      username: ['', [Validators.minLength(6), Validators.maxLength(20), Validators.required]],
    });
  }

  onDemenager(memberId: number) {
    this.ref = memberId;
    this.isDemenager = !this.isDemenager;
  }

  refreshInfo() {
    this.room$ = this.roomService.roomIdGet(this.room_id)
      .pipe(map(room => {
        this.memberIds$ = this.roomMemberService.roomIdMemberGet(this.room_id)
          .pipe(
            map(response => {
              for (let i of response) {
                this.cachedMemberUsernames.set(+i, this.memberService.memberIdGet(+i).pipe(shareReplay(1)));
              }
              return response
            })
          );
        return room;
      }));
    this.ports$ = this.portService.portGet(undefined, undefined, undefined, <AbstractPort>{ room: this.room_id });
  }

  onSubmitComeInRoom() {
    const v = this.EmmenagerForm.value;
    this.memberService.memberGet(1, 0, v.username)
      .subscribe((member_list) => {
        const member = member_list[0];
        this.roomMemberService.roomIdMemberAddPatch(this.room_id, { id: member })
          .subscribe((_) => {
            this.refreshInfo();
            this.notificationService.successNotification();
          });
      }, (_) => {
        this.notificationService.errorNotification(404, undefined, 'Member ' + v.username + ' does not exists');
      });
  }

  onSubmitMoveRoom(memberId: number) {
    const v = this.roomForm.value;

    this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{ roomNumber: v.roomNumberNew })
      .subscribe(rooms => {
        if (rooms.length == 0) {
          this.notificationService.errorNotification(404, undefined, "The room with number: " + v.roomNumberNew + " does not exists");
          return
        }
        const room = rooms[0];
        this.roomMemberService.roomIdMemberAddPatch(room.id, { id: memberId })
          .subscribe((_) => {
            this.refreshInfo();
            this.onDemenager(memberId);
            this.router.navigate(['room', 'view', v.roomNumberNew]);
            this.notificationService.successNotification();
          });
      })
  }

  onRemoveFromRoom(memberId: number) {
    this.roomMemberService.roomIdMemberDelPatch(this.room_id, { id: memberId })
      .subscribe((_) => {
        this.refreshInfo();
        this.notificationService.successNotification();
      });
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.room_id = +params['room_id'];
      this.refreshInfo();
    });
  }

  public getMemberUsername(id: number) {
    return this.cachedMemberUsernames.get(id)
  }
}
