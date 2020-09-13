import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {BehaviorSubject, combineLatest, Observable, timer} from 'rxjs';
import {AbstractDevice, Device, DeviceService, Member, MemberService, PaymentMethod, TransactionService} from '../api';
import {ActivatedRoute, Router} from '@angular/router';
import {NotificationsService} from 'angular2-notifications';
import {finalize, first, flatMap, map, share, switchMap, tap} from 'rxjs/operators';
import {Utils} from '../utils';

@Component({
  selector: 'app-member-details',
  templateUrl: './member-view.component.html',
  styleUrls: ['./member-view.component.css']
})

export class MemberViewComponent implements OnInit, OnDestroy {

  submitDisabled = false;
  date = new Date;
  getDhcp = false;
  member$: Observable<Member>;
  paymentMethods$: Observable<Array<PaymentMethod>>;
  all_devices$: Observable<Device[]>;
  log$: Observable<Array<string>>;
  macHighlighted$: Observable<string>;
  cotisation = false;
  private refreshInfoOrder$ = new BehaviorSubject<null>(null);
  private member_id$: Observable<number>;
  private commentForm: FormGroup;
  private deviceForm: FormGroup;
  private subscriptionForm: FormGroup;
  private selectedDevice: string;
  private options = {year: 'numeric', month: 'long', day: 'numeric'};
  private amountToPay = 0;
  private content: string;  // for log formatting
  private subscriptionPrices: number[] = [0, 9, 18, 27, 36, 45, 50];

  constructor(
    public memberService: MemberService,
    public deviceService: DeviceService,
    public transactionService: TransactionService,
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private notif: NotificationsService,
  ) {
    this.createForm();
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
      tap((user) => this.commentForm.setValue({comment: (user.comment === undefined) ? '' : user.comment})),
      share(),
    );

    this.all_devices$ = refresh$.pipe(
      switchMap(member_id => this.deviceService.deviceGet(undefined, undefined, '', <AbstractDevice>{member: member_id})),
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
  }

  ngOnDestroy() {
  }

  refreshInfo(): void {
    this.refreshInfoOrder$.next(null);
  }

  // switchMap(username => this.memberService.memberUsernameGet(username)),
  // tap((user) => this.commentForm.setValue({comment: (user.comment === undefined) ? '' : user.comment})),
  // share(),

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
    this.subscriptionForm = this.fb.group({
      renewal: ['0', [Validators.required]],
      checkCable3: [false],
      checkCable5: [false],
      checkAdapter: [false],
      paidBy: ['0', [Validators.required]],
    });
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

  submitSubscription(): void {
    // TODO
  }


  addDevice(member_id?: number, alreadyExists?: boolean) {
    if (member_id === undefined) {
      return this.member_id$
        .pipe(
          flatMap((usr) => this.addDevice(usr))
        );
    }

    const v = this.deviceForm.value;
    const mac = Utils.sanitizeMac(v.mac);

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
          return this.all_devices$;
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
          return this.all_devices$;
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

  formatDate(monthsToAdd: number) {
    this.date = new Date();
    this.date.setMonth(this.date.getMonth() + monthsToAdd);

    return this.date.toLocaleDateString('fr-FR', this.options);
  }

  updateAmount() {
    this.amountToPay = 0;
    this.amountToPay = this.amountToPay + this.subscriptionPrices[this.subscriptionForm.value.renewal];

    if (this.subscriptionForm.value.checkCable3 === true) {
      this.amountToPay = this.amountToPay + 3;
    }
    if (this.subscriptionForm.value.checkCable5 === true) {
      this.amountToPay = this.amountToPay + 5;
    }
    if (this.subscriptionForm.value.checkAdapter === true) {
      this.amountToPay = this.amountToPay + 13;
    }
  }

}
