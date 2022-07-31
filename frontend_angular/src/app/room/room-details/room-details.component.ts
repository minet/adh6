import { Component, OnDestroy, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AbstractMember, AbstractPort, Member, MemberService, Port, PortService, Room, RoomService, AbstractRoom } from '../../api';
import { map, takeWhile } from 'rxjs/operators';
import { Location } from '@angular/common';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-room-details',
  templateUrl: './room-details.component.html',
  styleUrls: ['./room-details.component.css']
})
export class RoomDetailsComponent implements OnInit, OnDestroy {

  disabled = false;
  room$: Observable<AbstractRoom>;
  ports$: Observable<Array<AbstractPort>>;
  members$: Observable<Array<AbstractMember>>;
  room_id: number;
  room_number: number;
  roomForm: FormGroup;
  EmmenagerForm: FormGroup;
  public isDemenager = false;
  public ref: string;
  private alive = true;
  private sub: any;

  constructor(
    private location: Location,
    private notificationService: NotificationService,
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
      roomNumberNew: ['', [Validators.min(-1), Validators.max(9999), Validators.required]],
    });
    this.EmmenagerForm = this.fb.group({
      username: ['', [Validators.minLength(6), Validators.maxLength(20), Validators.required]],
    });
  }

  onDemenager(username: string) {
    this.ref = username;
    this.isDemenager = !this.isDemenager;
  }

  refreshInfo() {
    this.room$ = this.roomService.roomIdGet(this.room_id)
      .pipe(map(room => {
        this.room_number = room.roomNumber;
        this.members$ = this.memberService.memberGet(undefined, undefined, undefined, <AbstractMember>{ roomNumber: this.room_number });
        return room;
      }));
    this.ports$ = this.portService.portGet(undefined, undefined, undefined, <AbstractPort>{ room: this.room_id });
  }

  onSubmitComeInRoom() {
    const v = this.EmmenagerForm.value;
    this.memberService.memberGet(1, 0, v.username)
      .pipe(takeWhile(() => this.alive))
      .subscribe((member_list) => {
        const member = member_list[0];
        this.memberService.memberIdPatch(member, <Member>{
          roomNumber: this.room_number
        })
          .pipe(takeWhile(() => this.alive))
          .subscribe((_) => {
            this.refreshInfo();
            this.notificationService.successNotification();
          });
      }, (_) => {
        this.notificationService.errorNotification(404, undefined, 'Member ' + v.username + ' does not exists');
      });
  }

  onSubmitMoveRoom(username: string) {
    const v = this.roomForm.value;

    this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{ roomNumber: v.roomNumberNew })
      .subscribe(rooms => {
        if (rooms.length == 0) {
          this.notificationService.errorNotification(404, undefined, "The room with number: " + v.roomNumberNew + " does not exists");
          return
        }
        const room = rooms[0];
        this.memberService.memberGet(1, 0, undefined, <AbstractMember>{ username: username })
          .subscribe((members) => {
            if (members.length == 0) {
              this.notificationService.errorNotification(404, undefined, 'Member ' + v.username + ' does not exists');
              return
            }
            const member = members[0];
            console.log(member);
            this.memberService.memberIdPatch(member.id, <AbstractMember>{ roomNumber: room.roomNumber }, 'response')
              .subscribe((_) => {
                this.refreshInfo();
                this.onDemenager(username);
                this.router.navigate(['room', 'view', v.roomNumberNew]);
                this.notificationService.successNotification();
              });
          });
      })
  }

  onRemoveFromRoom(username: string) {
    this.memberService.memberGet(1, 0, undefined, <AbstractMember>{ username: username })
      .subscribe((members) => {
        if (members.length == 0) {
          this.notificationService.errorNotification(404, undefined, 'Member ' + username + ' does not exists');
          return
        }
        const member = members[0];
        this.memberService.memberIdPatch(member.id, <AbstractMember>{ roomNumber: -1 }, 'response')
          .subscribe((_) => {
            this.refreshInfo();
            this.location.back();
            this.notificationService.successNotification();
          });
      });
  }

  onDelete() {
    this.roomService.roomIdDelete(this.room_id, 'response')
      .pipe(takeWhile(() => this.alive))
      .subscribe((_) => {
        this.router.navigate(['room']);
        this.notificationService.successNotification();
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
