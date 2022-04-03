import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BehaviorSubject, combineLatest, Observable, timer } from 'rxjs';
import { AbstractDevice, AbstractMembership, AccountService, Device, DeviceService, RoomService, Member, MemberService, Membership, MembershipService, PaymentMethod, TransactionService, AbstractRoom, Room, AbstractMember } from '../../api';
import { ActivatedRoute } from '@angular/router';
import { finalize, first, flatMap, map, share, switchMap, tap } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';
import { ListComponent } from '../../member-device/list/list.component';

@Component({
  selector: 'app-member-details',
  templateUrl: './member-view.component.html',
  styleUrls: ['./member-view.component.css']
})

export class MemberViewComponent implements OnInit, OnDestroy {
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
  newMembershipDisabled = false;
  public moveIn: boolean = false;
  public moveInDisabled: boolean = false;

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
      switchMap(member_id => this.memberService.memberMemberIdGet(member_id)),
      tap((user) => this.commentForm.setValue({ comment: (user.comment === undefined) ? '' : user.comment })),
      share(),
    );

    this.log$ = this.member_id$.pipe(
      switchMap((str) => {
        return timer(0, 10 * 1000).pipe(
          switchMap(() => this.memberService.memberMemberIdLogsGet(str, this.getDhcp, 'body', false, false))
        );
      }) // refresh every 10 secs
    );

    this.paymentMethods$ = this.transactionService.paymentMethodGet();

    this.latestMembership$ = refresh$.pipe(
      switchMap(member_id => this.membershipService.getLatestMembership(member_id, 'body'))
    )
  }

  validatePayment(membershipUUID: string, status: AbstractMembership.StatusEnum, memberID: number): void {
    this.cotisation = false;
    this.membershipService.membershipValidate(+memberID, membershipUUID).subscribe(() => {
      this.refreshLatestMembership(memberID);
    });
  }

  ngOnDestroy() {
  }

  refreshInfo(): void {
    this.refreshInfoOrder$.next(null);
  }

  refreshLog(): void {
    // stream, which will emit the username every time the profile needs to be refreshed
    const refresh$ = combineLatest([this.member_id$, this.refreshInfoOrder$])
      .pipe(
        map(([x]) => x),
      );

    this.log$ = this.member_id$.pipe(
      switchMap((str) => {
        return timer(0, 10 * 1000).pipe(
          switchMap(() => this.memberService.memberMemberIdLogsGet(str, this.getDhcp))
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

  newMembership(member_id: number): void {
    this.latestMembership$ = this.membershipService.memberMemberIdMembershipPost(<Membership>{
      member: member_id,
      status: AbstractMembership.StatusEnum.INITIAL
    }, member_id, 'body').pipe(
      finalize(() => {
        this.newMembershipDisabled = false;
        this.refreshLatestMembership(member_id);
      }),
      first(() => this.newMembershipDisabled = true)
    );
  }

  refreshLatestMembership(member_id: number): void {
    this.latestMembership$ = this.membershipService.getLatestMembership(+member_id, 'body');
  }

  submitComment(): void {
    this.submitDisabled = true;
    const newComment = this.commentForm.value.comment;

    this.member$.pipe(
      map(user => {
        user.comment = newComment;
        return user;
      }),
      flatMap(user => this.memberService.memberMemberIdPut(user, user.id)),
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

  addDevice(member_id?: number, alreadyExists?: boolean) {
    if (member_id === undefined) {
      return this.member_id$
        .pipe(
          flatMap((usr) => this.addDevice(usr))
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
        flatMap(() => {
          this.refreshInfo();
          return null; // @TODO return the device ?
        }),
        map(() => null)
      );
  }

  deviceDelete(device_id: number): void {
    this.submitDisabled = true;
    this.deviceService.deviceDeviceIdDelete(device_id)
      .pipe(
        first(),
        flatMap(() => {
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
        return '<font color="green">' + match + '</font>';
      });
    } else if (this.content.includes('Login incorrect')) {
      return this.content.replace(new RegExp('Login incorrect', 'gi'), match => {
        return '<font color="red">' + match + '</font>';
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

            this.memberService.memberMemberIdPatch(<AbstractMember>{ room: room.id }, memberId, 'response')
              .subscribe((response) => {
                this.refreshInfo();
                this.moveIn = false;
                this.notificationService.successNotification();
              })
          })
      })
  }
}
