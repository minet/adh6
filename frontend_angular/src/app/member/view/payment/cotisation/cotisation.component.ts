import {Component, Input, Output, EventEmitter} from "@angular/core";
import {
  AbstractAccount,
  AbstractMember,
  AccountService,
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
import {Toast} from "../../../../notification.service";

interface SubscriptionForm {
  paidWith: FormControl<number | null>;
  durationIndex: FormControl<number | null>;
}

@Component({
  imports: [ReactiveFormsModule],
  selector: "app-cotisation",
  templateUrl: "./cotisation.component.html",
})
export class CotisationComponent {
  @Input() member?: AbstractMember;
  @Input() paymentMethods?: PaymentMethod[];
  @Output() updateSubscription = new EventEmitter<boolean>();

  public subscriptionForm: FormGroup<SubscriptionForm> = new FormGroup({
    paidWith: new FormControl(-1, [Validators.min(1)]),
    durationIndex: new FormControl(-1, [Validators.min(0)]),
  });
  public needSignature = false;
  public needValidation = false;

  // The last one is necessaraly without a room
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
    private readonly accountService: AccountService,
  ) {}

  public get amount(): number {
    const durationIndex = this.subscriptionForm.value.durationIndex;
    return durationIndex !== null &&
      durationIndex !== undefined &&
      durationIndex !== -1
      ? this.subscriptionPrices.at(durationIndex) || 0
      : 0;
  }

  public submitSubscription() {
    const v = this.subscriptionForm.value;

    // Validate form values
    if (
      !this.member?.id ||
      v.durationIndex == null ||
      v.paidWith == null ||
      v.durationIndex < 0 ||
      v.paidWith < 1
    ) {
      void Toast.fire("Veuillez remplir tous les champs requis");
      return;
    }

    // Case where there is no subscription
    this.accountService
      .accountGet(1, 0, undefined, <AbstractAccount>{
        member: this.member.id,
      })
      .subscribe({
        next: (response) => {
          if (response.length == 0) {
            void Toast.fire("No Account found");
            return;
          }
          console.log(response[0]);
          const subscription: SubscriptionBody = {
            duration: this.subscriptionDuration.at(v.durationIndex!)!,
            account: response[0].id,
            paymentMethod: v.paidWith!,
            member: this.member!.id!,
            hasRoom: v.durationIndex !== this.subscriptionPrices.length - 1,
          };
          if (this.isSubscriptionFinished) {
            this.membershipService
              .memberIdSubscriptionPost(this.member!.id!, subscription, "body")
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
                  void Toast.fire("Inscription créée");
                  this.updateSubscription.emit(true);
                },
                error: (error) => {
                  console.error("Error creating subscription:", error);
                  void Toast.fire(
                    "Erreur lors de la création de l'inscription",
                  );
                },
              });
          } else {
            this.membershipService
              .memberIdSubscriptionPatch(this.member!.id!, subscription)
              .subscribe({
                next: () => {
                  void Toast.fire("Inscription mise à jour");
                  this.updateSubscription.emit(true);
                },
                error: (error) => {
                  console.error("Error updating subscription:", error);
                  void Toast.fire(
                    "Erreur lors de la mise à jour de l'inscription",
                  );
                },
              });
          }
        },
        error: (error) => {
          console.error("Error fetching account:", error);
          void Toast.fire("Erreur lors de la récupération du compte");
        },
      });
  }

  formatDate(monthsToAdd: number): string {
    const departureDate = this.member?.departureDate;
    const date =
      departureDate && new Date().getTime() < new Date(departureDate).getTime()
        ? new Date(departureDate)
        : new Date();
    date.setMonth(date.getMonth() + monthsToAdd);
    return date.toLocaleDateString("fr-FR", this.options);
  }

  get isSubscriptionFinished(): boolean {
    return (
      this.member?.membership === AbstractMembership.StatusEnum.Complete ||
      this.member?.membership === AbstractMembership.StatusEnum.Cancelled ||
      this.member?.membership === AbstractMembership.StatusEnum.Aborted
    );
  }
}
