import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormArray, FormBuilder, FormGroup, Validators} from '@angular/forms';
import {BehaviorSubject, combineLatest, forkJoin, merge, Observable, timer} from 'rxjs';
import {AbstractDevice, AbstractMembership, AccountService, Device, DeviceService, Member, MemberService, Membership, MembershipService, PaymentMethod, TransactionService, AbstractAccount, Account, Product, TreasuryService} from '../api';
import {ActivatedRoute, Router} from '@angular/router';
import {NotificationsService} from 'angular2-notifications';
import {finalize, first, flatMap, map, mergeMap, share, switchMap, tap} from 'rxjs/operators';
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
  latestMembership$: Observable<Membership>;
  products$: Observable<Product[]>;
  log$: Observable<Array<string>>;
  macHighlighted$: Observable<string>;
  cotisation = false;
  newMembershipDisabled = false;
  private refreshInfoOrder$ = new BehaviorSubject<null>(null);
  private member_id$: Observable<number>;
  private commentForm: FormGroup;
  private deviceForm: FormGroup;
  private subscriptionForm: FormGroup;
  private selectedDevice: string;
  private options: Intl.DateTimeFormatOptions = {year: 'numeric', month: 'long', day: 'numeric'};
  private amountToPay = 0;
  private content: string;  // for log formatting
  private subscriptionPrices: number[] = [0, 9, 18, 27, 36, 45, 50, 9];
  private subscriptionDuration: AbstractMembership.DurationEnum[] = [0, 1, 2, 3, 4, 5, 12, 12];

  statusToText = {
    'PENDING_RULES': "Sign the Charter",
    'PENDING_PAYMENT_INITIAL': "Select Duration of payment",
    'PENDING_PAYMENT': "Select Account to pay with",
    'PENDING_PAYMENT_VALIDATION': "Need manual validation",
  }

  constructor(
    public memberService: MemberService,
    public membershipService: MembershipService,
    public deviceService: DeviceService,
    public transactionService: TransactionService,
    public accountService: AccountService,
    private treasuryService: TreasuryService,
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private notif: NotificationsService,
  ) {
    this.createForm();
  }

  signCharter(): void {
    this.member_id$.subscribe((member_id) => {
      console.log(member_id);
      this.memberService.charterPut(member_id, 1, "body").subscribe(() => console.log("Charter  Signed"));
    })
  }

  get productsFormArray(): FormArray {
    return this.subscriptionForm.get('products') as FormArray
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

    this.products$ = this.treasuryService.productGet(100, 0, undefined, "body");
    this.products$.subscribe((products) => {
      products.forEach((product) => {
        this.productsFormArray.push(this.fb.group({
          id: [{value: product.id}],
          checked: [false, [Validators.required]],
          amount: [{value: product.sellingPrice}]
        }))
      })
    });
  }

  checkMembershipStatus(status: AbstractMembership.StatusEnum): boolean {
    return !(
      status == AbstractMembership.StatusEnum.ABORTED ||
      status == AbstractMembership.StatusEnum.CANCELLED ||
      status == AbstractMembership.StatusEnum.COMPLETE
    )
  }

  actionMembershipStatus(membershipUUID: string, status: AbstractMembership.StatusEnum, memberID: number): void {
    switch (status) {
      case AbstractMembership.StatusEnum.PENDINGPAYMENTVALIDATION:
        this.membershipService.membershipValidate(+memberID, membershipUUID).subscribe(() => {
          this.refreshLatestMembership(memberID);
        });
        break
    }
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
      products: this.fb.array([]),
      paidBy: ['0', [Validators.required]],
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

  submitSubscription(): void {
    this.member_id$.subscribe((member_id) => this.addSubscription(member_id));
  }

  addSubscription(member_id: number) {
    const v = this.subscriptionForm.value;
    let products = [];
    for (let i = 0; i < this.productsFormArray.length; i++) {
      if (this.productsFormArray.at(i).value.checked === true) {
        products.push(+this.productsFormArray.at(i).value.id.value)
      }
    }

    const abstractAccount: AbstractAccount = {
      member: member_id
    };
    this.accountService.accountGet(1, 0, undefined, abstractAccount, 'response')
      .subscribe((response) => {
        if (+response.headers.get('x-total-count') == 0) { 
          this.notif.alert("No Account", "There is no account selected for this subscription");
          return;
        }
        const account: Account = response.body[0]
        this.paymentMethods$.subscribe((paymentMethodList) => {
          let paymentMethod: PaymentMethod;
          paymentMethodList.forEach((elem) => {
            if (elem.id == +v.paidBy) { paymentMethod = elem }
          })
          const subscription: AbstractMembership = {
            duration: this.subscriptionDuration[v.renewal],
            account: account.id,
            products: products,
            paymentMethod: paymentMethod.id,
            hasRoom: +v.renewal !== 7
          }

          this.latestMembership$.subscribe((membership) => {
            this.membershipService.memberMemberIdMembershipUuidPatch(subscription, member_id, membership.uuid).subscribe(() => {
              this.refreshLatestMembership(member_id);
              this.toggleCotisationMenu();
            })
          })
        })
      })
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

  formatDate(monthsToAdd: number): string {
    this.date = new Date();
    this.date.setMonth(this.date.getMonth() + monthsToAdd);

    return this.date.toLocaleDateString('fr-FR', this.options);
  }

  updateAmount() {
    this.amountToPay = 0;
    this.amountToPay = this.amountToPay + this.subscriptionPrices[this.subscriptionForm.value.renewal];

    for (let i = 0; i < this.productsFormArray.length; i++) {
      if (this.productsFormArray.at(i).value.checked === true) {
        this.amountToPay += +this.productsFormArray.at(i).value.amount.value;
      }
    }
  }

}
