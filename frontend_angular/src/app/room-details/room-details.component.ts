import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {AbstractMember, AbstractPort, Member, MemberService, Port, PortService, Room, RoomService} from '../api';
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
      roomNumberNew: ['', [Validators.min(1000), Validators.max(9999), Validators.required]],
    });
    this.EmmenagerForm = this.fb.group({
      username: ['', [Validators.minLength(7), Validators.maxLength(8), Validators.required]],
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

    this.memberService.memberGet(1, 0, username)
      .pipe(takeWhile(() => this.alive))
      .subscribe((member_list) => {
        const member: Member = member_list[0];
        member.room = v.roomNumberNew;
        this.memberService.memberMemberIdPut(member, member.id, 'response')
          .pipe(takeWhile(() => this.alive))
          .subscribe((response) => {
            this.refreshInfo();
            this.onDemenager(username);
            this.router.navigate(['room', v.roomNumberNew]);
            this.notif.success(response.status + ': Success');
          });
      });
  }

  onRemoveFromRoom(username) {
    this.memberService.memberGet(1, 0, username)
      .pipe(takeWhile(() => this.alive))
      .subscribe((member_list) => {
        const member: Member = member_list[0];
        member.room = null;
        this.memberService.memberMemberIdPut(member, member.id, 'response')
          .pipe(takeWhile(() => this.alive))
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
