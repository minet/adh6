import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BehaviorSubject, combineLatest, Observable, timer } from 'rxjs';
import { AbstractDevice, AbstractMembership, AccountService, Device, DeviceService, RoomService, Member, MemberService, Membership, MembershipService, PaymentMethod, TransactionService, AbstractRoom, Room, AbstractMember } from '../../api';
import { ActivatedRoute } from '@angular/router';
import { finalize, first, map, share, switchMap, tap } from 'rxjs/operators';
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

  cotisation = false;
  submitDisabled = false;
  getDhcp = false;
  member$: Observable<Member>;
  paymentMethods$: Observable<Array<PaymentMethod>>;
  latestMembership$: Observable<Membership>;
  log$: Observable<Array<string>>;
  macHighlighted$: Observable<string>;
  public moveIn: boolean = false;
  public moveInDisabled: boolean = false;
  public showLogs = false;
  public room$: Observable<number>;

  private refreshInfoOrder$ = new BehaviorSubject<null>(null);
  private member_id$: Observable<number>;
  private commentForm: FormGroup;
  private moveInForm: FormGroup;
  private deviceForm: FormGroup;
  private selectedDevice: string;
  private content: string;  // for log formatting

  constructor(
    public memberService: MemberService,
    public membershipService: MembershipService,
    public roomService: RoomService,
    public deviceService: DeviceService,
    public transactionService: TransactionService,
    public accountService: AccountService,
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
      tap((user) => this.commentForm.setValue({ comment: (user.comment === undefined) ? '' : user.comment })),
      share(),
    );

    this.log$ = this.member_id$.pipe(
      switchMap((str) => {
        return timer(0, 10 * 1000).pipe(
          switchMap(() => this.memberService.memberIdLogsGet(str, this.getDhcp, 'body', false, false))
        );
      }) // refresh every 10 secs
    );

    this.paymentMethods$ = this.transactionService.paymentMethodGet();

    this.latestMembership$ = refresh$.pipe(
      switchMap(member_id => this.membershipService.getLatestMembership(member_id, undefined, 'body'))
    )
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

  toggleCotisationMenu(): void {
    this.cotisation = !this.cotisation;
  }

  createForm(): void {
    this.commentForm = this.fb.group({
      comment: [''],
    });
    this.deviceForm = this.fb.group({
      mac: ['01-23-45-76-89-AB', [Validators.required, Validators.minLength(17), Validators.maxLength(17)]],
      connectionType: ['wired', Validators.required],
    });
    this.moveInForm = this.fb.group({
      roomNumber: ['', [Validators.required, Validators.min(-1), Validators.max(9999)]]
    });
  }

  refreshLatestMembership(member_id: number): void {
    this.latestMembership$ = this.membershipService.getLatestMembership(+member_id, undefined, 'body');
  }

  submitComment(): void {
    this.submitDisabled = true;
    const newComment = this.commentForm.value.comment;

    this.member$.pipe(
      map(user => {
        user.comment = newComment;
        return user;
      }),
      map(user => this.memberService.memberIdPut(user, user.id)),
      map(() => {
        this.refreshInfo();
        return null;
      }),
      finalize(() => this.submitDisabled = false),
      first(),
    ).subscribe(() => {
    });

    // will trigger the refresh of member$ and thus the update of the comment
    this.refreshInfo();
  }

  submitDevice(): void {
    // First we fetch the username of the current user...
    this.submitDisabled = true;
    this.addDevice()
      .pipe(
        first(),
        // No matter what, submit will be re-enable (even if there is an error)
        finalize(() => this.submitDisabled = false),
      )
      .subscribe(() => {
      });
  }

  addDevice(member_id?: number) {
    if (member_id === undefined) {
      return this.member_id$
        .pipe(
          map((usr) => this.addDevice(usr))
        );
    }

    const v = this.deviceForm.value;
    const mac = v.mac.toLowerCase().replace(/[^a-f0-9]+/g, '-');

    const device: AbstractDevice = {
      mac: mac,
      connectionType: v.connectionType,
      member: Number(member_id)
    };

    // Make an observable that will return True if the device already exists
    // If the device does not then create it, and refresh the info
    return this.deviceService.devicePost(device)
      .pipe(
        map(() => {
          this.refreshInfo();
          return null; // @TODO return the device ?
        }),
        map(() => null)
      );
  }

  deviceDelete(device_id: number): void {
    this.submitDisabled = true;
    this.deviceService.deviceIdDelete(device_id)
      .pipe(
        first(),
        map(() => {
          this.refreshInfo();
          return null; // @TODO return the device ?
        }),
        first(),
        finalize(() => this.submitDisabled = false)
      )
      .subscribe(() => {
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


  toggleDeviceDetails(device: Device): void {
    if (this.isDeviceOpened(device)) {
      this.selectedDevice = null;
    } else {
      this.selectedDevice = device.mac;
    }
  }

  isDeviceOpened(device: Device): boolean {
    return this.selectedDevice === device.mac;
  }

  refreshMembership(memberId: number): void {
    this.latestMembership$ = this.membershipService.getLatestMembership(memberId);
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
