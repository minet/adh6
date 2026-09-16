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
import {CONFIG_STATE_LABELS, MODEL_LABELS} from "./labels";

const MAC_PATTERN = /^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$/;
const IPV4_PATTERN =
  /^((25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(25[0-5]|2[0-4]\d|1?\d?\d)$/;

/** Creates a mini-router, or updates it when one is given. */
@Component({
  selector: "app-mini-router-form",
  imports: [ReactiveFormsModule],
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
    mac: new FormControl("", {
      nonNullable: true,
      validators: Validators.pattern(MAC_PATTERN),
    }),
    ip: new FormControl("", {
      nonNullable: true,
      validators: Validators.pattern(IPV4_PATTERN),
    }),
    model: new FormControl<MiniRouter.ModelEnum>("beryl_giga", {
      nonNullable: true,
    }),
    configState: new FormControl<MiniRouter.ConfigStateEnum>("not_pimped", {
      nonNullable: true,
    }),
    comment: new FormControl("", {nonNullable: true}),
  });
  submitting = false;

  private readonly miniRouterService = inject(MiniRouterService);
  private readonly notificationService = inject(NotificationService);

  ngOnChanges(): void {
    if (this.miniRouter) {
      this.form.reset({
        hardwareMac: this.miniRouter.hardwareMac,
        mac: this.miniRouter.mac ?? "",
        ip: this.miniRouter.ip ?? "",
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
      mac: v.mac.trim() || null,
      ip: v.ip.trim() || null,
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
            ? $localize`:@@mini-router.form.duplicate:Un mini-routeur utilise déjà cette adresse MAC ou IP.`
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
