import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {AbstractMember, AbstractPort, Member, MemberService, Port, PortService, Room, RoomService, AbstractRoom} from '../api';
import {NotificationsService} from 'angular2-notifications';
import {takeWhile} from 'rxjs/operators';

@Component({
  selector: 'app-room-details',
  templateUrl: './room-details.component.html',
  styleUrls: ['./room-details.component.css']
})
export class RoomDetailsComponent implements OnInit, OnDestroy {

  disabled = false;
  authenth = false;
  room$: Observable<Room>;
  ports$: Observable<Array<Port>>;
  members$: Observable<Array<Member>>;
  room_id: number;
  roomForm: FormGroup;
  EmmenagerForm: FormGroup;
  public isEmmenager = false;
  public isDemenager = false;
  public ref: string;
  private alive = true;
  private sub: any;

  constructor(
    private notif: NotificationsService,
    private router: Router,
    public roomService: RoomService,
    public portService: PortService,
    public memberService: MemberService,
    private fb: FormBuilder,
    private route: ActivatedRoute,
  ) {
    this.createForm();
  }

  createForm() {
    this.ngOnInit();
    this.roomForm = this.fb.group({
      roomNumberNew: ['', [Validators.min(0), Validators.max(9999), Validators.required]],
    });
    this.EmmenagerForm = this.fb.group({
      username: ['', [Validators.minLength(6), Validators.maxLength(20), Validators.required]],
    });
  }

  auth() {
    this.authenth = !this.authenth;
  }

  onEmmenager() {
    this.isEmmenager = !this.isEmmenager;
  }

  onDemenager(username) {
    this.ref = username;
    this.isDemenager = !this.isDemenager;
  }

  refreshInfo() {
    this.room$ = this.roomService.roomRoomIdGet(this.room_id);
    this.ports$ = this.portService.portGet(undefined, undefined, '', <AbstractPort>{room: this.room_id});
    this.members$ = this.memberService.memberGet(undefined, undefined, '', <AbstractMember>{room: this.room_id});
  }

  onSubmitComeInRoom() {
    const v = this.EmmenagerForm.value;
    this.memberService.memberGet(1, 0, v.username)
      .pipe(takeWhile(() => this.alive))
      .subscribe((member_list) => {
        const member: Member = member_list[0];
        member.room = this.room_id;
        this.memberService.memberMemberIdPut(member, member.id, 'response')
          .pipe(takeWhile(() => this.alive))
          .subscribe((response) => {
            this.refreshInfo();
            this.notif.success(response.status + ': Success');
            this.onEmmenager();
          });
      }, (member) => {
        this.notif.error('Member ' + v.username + ' does not exists');
      });
  }

  onSubmitMoveRoom(username) {
    const v = this.roomForm.value;

    this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{roomNumber: v.roomNumberNew})
      .subscribe(rooms => {
        if (rooms.length == 0) {
          this.notif.alert("404", "The room does not exists");
          return
        }
        const room: Room = rooms[0];
        this.memberService.memberGet(1, 0, undefined, <AbstractMember>{username: username})
          .subscribe((members) => {
            if (members.length == 0) {
              this.notif.alert("404", "The member " + username + " does not exists");
              return
            }
            const member: Member = members[0];
            console.log(member);
            this.memberService.memberMemberIdPatch(<AbstractMember>{room: room.id}, member.id, 'response')
              .subscribe((response) => {
                this.refreshInfo();
                this.onDemenager(username);
                this.router.navigate(['room', v.roomNumberNew]);
                this.notif.success(response.status + ': Success');
              });
          });
      })
  }

  onRemoveFromRoom(username) {
    this.memberService.memberGet(1, 0, undefined, <AbstractMember>{username: username})
      .subscribe((members) => {
        if (members.length == 0) {
          this.notif.alert("404", "The member " + username + " does not exists");
          return
        }
        const member: Member = members[0];

        this.memberService.memberMemberIdPatch(<AbstractMember>{room: undefined}, member.id, 'response')
          .subscribe((response) => {
            this.refreshInfo();
            this.notif.success(response.status + ': Success');
          });
      });
  }

  onDelete() {
    this.roomService.roomRoomIdDelete(this.room_id, 'response')
      .pipe(takeWhile(() => this.alive))
      .subscribe((response) => {
        this.router.navigate(['room']);
        this.notif.success(response.status + ': Success');
      });
  }


  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.room_id = +params['room_id'];
      this.refreshInfo();
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

}
