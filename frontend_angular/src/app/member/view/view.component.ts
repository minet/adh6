import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BehaviorSubject, combineLatest, Observable, timer } from 'rxjs';
import { AbstractMembership, RoomService, Member, MemberService, Membership, AbstractRoom, Room, AbstractMember } from '../../api';
import { ActivatedRoute } from '@angular/router';
import { map, share, switchMap } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';
import { ListComponent } from '../../member-device/list/list.component';

@Component({
  selector: 'app-details',
  templateUrl: './view.component.html',
  styleUrls: ['./view.component.css']
})

export class ViewComponent implements OnInit {
  @ViewChild(ListComponent) wiredList: ListComponent;
  @ViewChild(ListComponent) wirelessList: ListComponent;

  currentTab = "profile";

  submitDisabled = false;
  getDhcp = false;
  member$: Observable<Member>;
  log$: Observable<Array<string>>;
  macHighlighted$: Observable<string>;
  public moveIn: boolean = false;
  public moveInDisabled: boolean = false;
  public showLogs = false;
  public room$: Observable<number>;

  private refreshInfoOrder$ = new BehaviorSubject<null>(null);
  private member_id$: Observable<number>;
  private moveInForm: FormGroup;
  private content: string;  // for log formatting

  constructor(
    public memberService: MemberService,
    public roomService: RoomService,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private notificationService: NotificationService,
  ) {
    this.createForm();
  }

  public parseMembershipStatus(membership: Membership): string {
    switch (membership.status) {
      case AbstractMembership.StatusEnum.PENDINGRULES:
        return "en attente de la signature de la charte"
      case AbstractMembership.StatusEnum.PENDINGPAYMENTINITIAL:
        return "en attente de la cotisation"
      case AbstractMembership.StatusEnum.PENDINGPAYMENT:
        return "en attente d'un moyen de payment et d'un compte"
      case AbstractMembership.StatusEnum.PENDINGPAYMENTVALIDATION:
        return "en attente de bonne prise en compte du payment"
    }
  }

  ngOnInit() {
    this.member_id$ = this.route.params.pipe(
      map(params => params['member_id'])
    );

    this.macHighlighted$ = this.route.queryParams.pipe(
      map(params => params['highlight'])
    );

    // stream, which will emit the username every time the profile needs to be refreshed
    const refresh$ = combineLatest([this.member_id$, this.refreshInfoOrder$])
      .pipe(
        map(([x]) => x),
      );

    this.member$ = refresh$.pipe(
      switchMap(member_id => this.memberService.memberIdGet(member_id)
        .pipe(map((user) => {
          this.room$ = this.roomService.roomGet(1, 0, undefined, (user.roomNumber !== undefined) ? <AbstractRoom>{ roomNumber: user.roomNumber } : undefined, ["id"])
            .pipe(
              map(rooms => {
                if (rooms.length != 1) {
                  this.notificationService.errorNotification(404, "Room with number " + user.roomNumber + " not found")
                  return undefined;
                }
                return rooms[0].id;
              })
            )
          return user;
        }))),
      share(),
    );

    this.log$ = this.member_id$.pipe(
      switchMap((str) => {
        return timer(0, 10 * 1000).pipe(
          switchMap(() => this.memberService.memberIdLogsGet(str, this.getDhcp, 'body', false, false))
        );
      }) // refresh every 10 secs
    );
  }

  refreshInfo(): void {
    this.refreshInfoOrder$.next(null);
  }

  refreshLog(): void {
    this.log$ = this.member_id$.pipe(
      switchMap((str) => {
        return timer(0, 10 * 1000).pipe(
          switchMap(() => this.memberService.memberIdLogsGet(str, this.getDhcp))
        );
      }) // refresh every 10 secs
    );
  }

  createForm(): void {
    this.moveInForm = this.fb.group({
      roomNumber: ['', [Validators.required, Validators.min(-1), Validators.max(9999)]]
    });
  }

  extractDateFromLog(log: string): Date {
    return new Date(log.split(' ')[0]);
  }

  extractMsgFromLog(log: string): string {
    this.content = ' ' + log.substr(log.indexOf(' ') + 1);

    if (this.content.includes('Login OK')) {
      return this.content.replace(new RegExp('Login OK:', 'gi'), match => {
        return '<font color="green">'.concat(match).concat('</font>');
      });
    } else if (this.content.includes('Login incorrect')) {
      return this.content.replace(new RegExp('Login incorrect', 'gi'), match => {
        return '<font color="red">'.concat(match).concat('</font>');
      });
    } else {
      return this.content;
    }
  }

  collapseMoveIn(): void {
    this.moveIn = !this.moveIn;
  }

  submitRoom(): void {
    const v = this.moveInForm.value;
    this.member_id$
      .subscribe(memberId => {
        this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{ roomNumber: +v.roomNumber })
          .subscribe(rooms => {
            if (rooms.length == 0) {
              this.notificationService.errorNotification(
                404,
                'No Room',
                'There is no room with this number'
              )
              return;
            }
            const room: Room = rooms[0];

            this.memberService.memberIdPatch(<AbstractMember>{ roomNumber: room.roomNumber }, memberId, 'response')
              .subscribe((_) => {
                this.refreshInfo();
                this.moveIn = false;
                this.notificationService.successNotification();
              })
          })
      })
  }
}
