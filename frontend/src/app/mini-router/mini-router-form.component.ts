import {
  Component,
  EventEmitter,
  inject,
  Input,
  OnChanges,
  Output,
} from "@angular/core";
import {HttpErrorResponse} from "@angular/common/http";
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {finalize} from "rxjs/operators";
import {MiniRouter, MiniRouterService} from "../api";
import {NotificationService} from "../notification.service";
import {detailOf} from "../shared/http-error";
import {addressesOf, MAX_NUMBER, MIN_NUMBER} from "./addresses";
import {CONFIG_STATE_LABELS, MODEL_LABELS} from "./labels";
import {MiniRouterAddressesComponent} from "./mini-router-addresses.component";

const MAC_PATTERN = /^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$/;

/** Creates a mini-router, or updates it when one is given. */
@Component({
  selector: "app-mini-router-form",
  imports: [ReactiveFormsModule, MiniRouterAddressesComponent],
  templateUrl: "./mini-router-form.component.html",
})
export class MiniRouterFormComponent implements OnChanges {
  @Input() miniRouter?: MiniRouter;
  @Output() saved = new EventEmitter<MiniRouter>();

  readonly models = Object.entries(MODEL_LABELS);
  readonly configStates = Object.entries(CONFIG_STATE_LABELS);
  readonly form = new FormGroup({
    hardwareMac: new FormControl("", {
      nonNullable: true,
      validators: [Validators.required, Validators.pattern(MAC_PATTERN)],
    }),
    number: new FormControl<number | null>(null, [
      Validators.min(MIN_NUMBER),
      Validators.max(MAX_NUMBER),
      Validators.pattern(/^\d+$/),
    ]),
    model: new FormControl<MiniRouter.ModelEnum>("beryl_giga", {
      nonNullable: true,
    }),
    configState: new FormControl<MiniRouter.ConfigStateEnum>("not_pimped", {
      nonNullable: true,
    }),
    comment: new FormControl("", {nonNullable: true}),
  });
  readonly minNumber = MIN_NUMBER;
  readonly maxNumber = MAX_NUMBER;
  submitting = false;

  get preview() {
    const number = this.form.controls.number;
    return number.value != null && number.valid
      ? addressesOf(number.value)
      : null;
  }

  private readonly miniRouterService = inject(MiniRouterService);
  private readonly notificationService = inject(NotificationService);

  ngOnChanges(): void {
    if (this.miniRouter) {
      this.form.reset({
        hardwareMac: this.miniRouter.hardwareMac,
        number: this.miniRouter.number ?? null,
        model: this.miniRouter.model,
        configState: this.miniRouter.configState,
        comment: this.miniRouter.comment ?? "",
      });
    }
  }

  onSubmit(): void {
    if (this.form.invalid || this.submitting) return;
    const v = this.form.getRawValue();
    const body: MiniRouter = {
      hardwareMac: v.hardwareMac.trim(),
      number: v.number ?? null,
      model: v.model,
      configState: v.configState,
      comment: v.comment.trim() || null,
    };
    const request$ =
      this.miniRouter?.id != null
        ? this.miniRouterService.miniRouterIdPut(this.miniRouter.id, body)
        : this.miniRouterService.miniRouterPost(body);

    this.submitting = true;
    request$.pipe(finalize(() => (this.submitting = false))).subscribe({
      next: (miniRouter) => {
        this.notificationService.successNotification();
        this.saved.emit(miniRouter);
      },
      error: (error: HttpErrorResponse) => {
        const message =
          error.status === 409
            ? $localize`:@@mini-router.form.duplicate:Un mini-routeur utilise déjà cette MAC constructeur ou ce numéro.`
            : detailOf(
                error,
                $localize`:@@mini-router.form.error:Impossible d'enregistrer le mini-routeur.`,
              );
        this.notificationService.errorNotification(
          error.status,
          undefined,
          message,
        );
      },
    });
  }
}
