import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AbstractMember, AbstractPort, MemberService, PortService, RoomService, AbstractRoom, RoomMembersService, Room } from '../../api';
import { map, shareReplay, switchMap } from 'rxjs/operators';
import { NotificationService, Toast } from '../../notification.service';

@Component({
  selector: 'app-room-details',
  templateUrl: './room-details.component.html'
})
export class RoomDetailsComponent implements OnInit {
  public room$: Observable<AbstractRoom>;
  public ports$: Observable<Array<AbstractPort>>;
  public memberLogins$: Observable<Array<string>>;
  public roomForm: UntypedFormGroup;
  public EmmenagerForm: UntypedFormGroup;
  public ref: string;
  public cachedMembers: Map<string, Observable<AbstractMember>> = new Map();

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
    this.roomForm = this.fb.group({
      roomNumberNew: ['', [Validators.min(-1), Validators.max(9999), Validators.required]],
    });
    this.EmmenagerForm = this.fb.group({
      username: ['', [Validators.minLength(6), Validators.maxLength(20), Validators.required]],
    });
  }

  refreshInfo() {
    this.memberLogins$ = this.room$.pipe(switchMap(room => this.roomMemberService.roomRoomNumberMemberGet(room.roomNumber)
      .pipe(
        map(response => {
          for (let i of response) {
            this.cachedMembers.set(i, this.memberService.memberGet(1, 0, i)
              .pipe(map(response => response[0]))
              .pipe(switchMap(r => this.memberService.memberIdGet(r)))
              .pipe(shareReplay(1)));
          }
          return response
        })
      )
    ));
    this.ports$ = this.room$.pipe(switchMap(room => this.portService.portGet(undefined, undefined, undefined, <AbstractPort>{ room: room.id })));
  }

  onSubmit() {
    const v = this.roomForm.value;
    this.roomMemberService.roomRoomNumberMemberPost(v.roomNumberNew, {login: this.ref})
      .subscribe(() => {
        this.ref = "";
        this.router.navigate(['/room', v.roomNumberNew, 'view']);
        Toast.fire("Adhérent déménagé", undefined, "success");
      });
  }

  onRemove(login: string) {
    this.roomMemberService.roomMemberLoginDelete(login)
      .subscribe(() => {
        this.refreshInfo();
        Toast.fire("Adhérent enlevé", undefined, "success");
      });
  }

  ngOnInit() {
    this.room$ = this.route.params.pipe(switchMap(params => {
      return this.roomService.roomRoomNumberGet(+params['room_number'], ["roomNumber", "vlan"]).pipe(shareReplay(1));
    }));
    this.refreshInfo();
  }
}
