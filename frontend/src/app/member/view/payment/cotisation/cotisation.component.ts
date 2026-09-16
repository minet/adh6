import {
  Component,
  Inject,
  Input,
  LOCALE_ID,
  Output,
  EventEmitter,
  OnDestroy,
  OnInit,
} from "@angular/core";
import {CharterService} from "../../../../api";
import {
  AbstractMember,
  AbstractMembership,
  MembershipService,
  PaymentMethod,
  SubscriptionBody,
} from "../../../../api";
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {NotificationService} from "../../../../notification.service";
import {environment} from "../../../../../environments/environment";
import {detailOf} from "../../../../shared/http-error";

interface SubscriptionForm {
  paidWith: FormControl<number | null>;
  durationIndex: FormControl<number | null>;
}

@Component({
  imports: [ReactiveFormsModule],
  selector: "app-cotisation",
  templateUrl: "./cotisation.component.html",
})
export class CotisationComponent implements OnInit, OnDestroy {
  /** Vrai tant que la charte n'est pas signee : pilote l'encart et le sondage. */
  public charterSigned: boolean | null = null;
  /** Affiche un discret « Verification... » pendant l'attente. */
  public checkingCharter = false;
  private charterPoll?: ReturnType<typeof setInterval>;
  /** Page compte Keycloak ou la charte est signee. */
  public readonly accountUrl = `${environment.SSO_URL}/account/`;

  @Input() member?: AbstractMember;
  @Input() paymentMethods?: PaymentMethod[];
  @Output() updateSubscription = new EventEmitter<boolean>();

  public subscriptionForm: FormGroup<SubscriptionForm> = new FormGroup({
    paidWith: new FormControl(-1, [Validators.min(1)]),
    durationIndex: new FormControl(-1, [Validators.min(0)]),
  });
  public needSignature = false;
  public needValidation = false;

  // The last one is necessarily without a room
  public subscriptionPrices: number[] = [9, 18, 27, 36, 45, 50, 9];
  public subscriptionDuration: AbstractMembership.DurationEnum[] = [
    1, 2, 3, 4, 5, 12, 12,
  ];

  private readonly options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };

  constructor(
    private readonly membershipService: MembershipService,
    private readonly charterService: CharterService,
    private readonly notificationService: NotificationService,
    @Inject(LOCALE_ID) private readonly locale: string,
  ) {}

  ngOnInit(): void {
    this.refreshCharter();
    // Keycloak records the signature with a direct SQL UPDATE, so nothing tells adh6 when it
    // happens. Polling is the only way for the page to notice while the permanencier waits with
    // the member in front of them. 10 seconds, not 5: the tab often stays open for minutes.
    this.charterPoll = setInterval(() => this.refreshCharter(), 10_000);
  }

  ngOnDestroy(): void {
    // Without this the interval outlives the tab and keeps querying forever.
    this.stopPolling();
  }

  private stopPolling(): void {
    if (this.charterPoll) {
      clearInterval(this.charterPoll);
      this.charterPoll = undefined;
    }
    this.checkingCharter = false;
  }

  /** Reads the signature date. A date means signed; empty or null means not yet. */
  private refreshCharter(): void {
    const id = this.member?.id;
    if (id == null || this.charterSigned) {
      return;
    }
    this.checkingCharter = true;
    this.charterService.charterCharterIdMemberIdGet(id, 1).subscribe({
      next: (signedAt) => {
        this.checkingCharter = false;
        if (typeof signedAt === "string" && signedAt.length > 0) {
          this.charterSigned = true;
          // Stop as soon as we know: no point hammering the API for the rest of the session.
          this.stopPolling();
        } else {
          this.charterSigned = false;
        }
      },
      error: () => {
        // A failed check must not break the page: the yellow notice simply stays.
        this.checkingCharter = false;
      },
    });
  }

  public get amount(): number {
    // The select hands over a string: "-1" !== -1, and .at(-1) would read the last price.
    const durationIndex = Number(
      this.subscriptionForm.value.durationIndex ?? -1,
    );
    return durationIndex >= 0
      ? this.subscriptionPrices.at(durationIndex) || 0
      : 0;
  }

  public submitSubscription() {
    const v = this.subscriptionForm.value;
    // A <select> with value="{{ }}" hands the form a string ("6", not 6): a strict comparison
    // against a number is then always false, and hasRoom was always sent as true.
    const durationIndex = Number(v.durationIndex);

    if (
      !this.member?.id ||
      v.durationIndex == null ||
      v.paidWith == null ||
      durationIndex < 0 ||
      v.paidWith < 1
    ) {
      this.notificationService.show(
        "warning",
        $localize`:@@common.required-fields:Veuillez remplir tous les champs requis`,
      );
      return;
    }

    const subscription: SubscriptionBody = {
      duration: this.subscriptionDuration.at(durationIndex)!,
      paymentMethod: +v.paidWith,
      member: this.member.id,
      hasRoom: !this.isWifiOnlyIndex(durationIndex),
    };

    if (this.isSubscriptionFinished) {
      this.membershipService
        .memberIdSubscriptionPost(this.member.id, subscription, "body")
        .subscribe({
          next: (m) => {
            if (m.status === AbstractMembership.StatusEnum.PendingRules) {
              this.needSignature = true;
            }
            if (
              m.status ===
              AbstractMembership.StatusEnum.PendingPaymentValidation
            ) {
              this.needSignature = false;
            }
            this.notificationService.successNotification(
              $localize`:@@subscription.created:Inscription créée`,
            );
            this.updateSubscription.emit(true);
          },
          error: (error) => {
            console.error("Error creating subscription:", error);
            this.notificationService.show(
              "danger",
              detailOf(
                error,
                $localize`:@@subscription.create.error:Erreur lors de la création de l'inscription`,
              ),
            );
          },
        });
    } else {
      this.membershipService
        .memberIdSubscriptionPatch(this.member.id, subscription)
        .subscribe({
          next: () => {
            this.notificationService.successNotification(
              $localize`:@@subscription.updated:Inscription mise à jour`,
            );
            this.updateSubscription.emit(true);
          },
          error: (error) => {
            console.error("Error updating subscription:", error);
            this.notificationService.show(
              "danger",
              detailOf(
                error,
                $localize`:@@subscription.update.error:Erreur lors de la mise à jour de l'inscription`,
              ),
            );
          },
        });
    }
  }

  formatDate(monthsToAdd: number): string {
    const departureDate = this.member?.departureDate;
    const date =
      departureDate && new Date().getTime() < new Date(departureDate).getTime()
        ? new Date(departureDate)
        : new Date();
    date.setMonth(date.getMonth() + monthsToAdd);
    return date.toLocaleDateString(this.locale, this.options);
  }

  get isSubscriptionFinished(): boolean {
    return (
      this.member?.membership === AbstractMembership.StatusEnum.Complete ||
      this.member?.membership === AbstractMembership.StatusEnum.Cancelled ||
      this.member?.membership === AbstractMembership.StatusEnum.Aborted
    );
  }

  get isPermanent(): boolean {
    return this.member?.permanent === true;
  }

  /** Human-readable label of the duration currently picked, for the recap. */
  get selectedDurationLabel(): string {
    const index = this.subscriptionForm.value.durationIndex;
    if (index == null || index < 0) {
      return $localize`:@@cotisation.duration.empty:aucune durée`;
    }
    return this.durationLabel(this.subscriptionDuration.at(index) ?? 0);
  }

  public durationLabel(months: number): string {
    return months === 12
      ? $localize`:@@cotisation.duration.year:1 an`
      : $localize`:@@cotisation.duration.months:${months}:months: mois`;
  }

  get visibleOptions(): {
    index: number;
    duration: AbstractMembership.DurationEnum;
    price: number;
  }[] {
    // Every member, wifi-only or not, can be given any subscription: validating a regular one
    // turns the wifi-only flag off (the member stays in room 666).
    return this.subscriptionDuration.map((duration, index) => ({
      index,
      duration,
      price: this.subscriptionPrices[index],
    }));
  }

  /** The last option is the wifi-only one: validating it moves the account to room 666. */
  public isWifiOnlyIndex(index: number): boolean {
    return index === this.subscriptionDuration.length - 1;
  }
}
