import {HttpErrorResponse} from "@angular/common/http";
import {Component, DestroyRef, inject, OnInit} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {ActivatedRoute, Router, RouterModule} from "@angular/router";
import {firstValueFrom, switchMap} from "rxjs";
import {AbstractSwitch, SwitchService} from "../../api";
import {NotificationService} from "../../notification.service";
import {DialogService} from "../../ui/dialog.service";

@Component({
  imports: [ReactiveFormsModule, RouterModule],
  selector: "app-switch-edit",
  templateUrl: "./switch-edit.component.html",
  styleUrls: ["./switch-edit.component.css"],
})
export class SwitchEditComponent implements OnInit {
  readonly switchForm = new FormGroup({
    description: new FormControl("", {
      nonNullable: true,
      validators: Validators.required,
    }),
    ip: new FormControl("", {
      nonNullable: true,
      validators: [
        Validators.required,
        Validators.pattern(/^(\d{1,3}\.){3}\d{1,3}$/),
      ],
    }),
    community: new FormControl("", {nonNullable: true}),
  });

  loading = true;
  saving = false;
  deleting = false;
  switchId: number | null = null;

  private readonly destroyRef = inject(DestroyRef);

  constructor(
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly switchService: SwitchService,
    private readonly notificationService: NotificationService,
    private readonly dialogService: DialogService,
  ) {}

  ngOnInit(): void {
    this.route.paramMap
      .pipe(
        switchMap((params) => {
          const rawId = params.get("switch_id");
          const id = rawId === null ? Number.NaN : Number(rawId);
          if (!Number.isSafeInteger(id) || id <= 0) {
            throw new Error("Switch ID parameter is invalid");
          }
          this.switchId = id;
          this.loading = true;
          return this.switchService.switchIdGet(id);
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (networkSwitch) => {
          this.switchForm.patchValue({
            description: networkSwitch.description ?? "",
            ip: networkSwitch.ip ?? "",
          });
          this.loading = false;
        },
        error: (error: unknown) => {
          this.loading = false;
          this.notifyError(
            error,
            $localize`:@@switch.edit.load-error:Impossible de charger le commutateur.`,
          );
        },
      });
  }

  async onSubmit(): Promise<void> {
    if (
      this.switchForm.invalid ||
      this.switchId === null ||
      this.saving ||
      this.deleting
    ) {
      this.switchForm.markAllAsTouched();
      return;
    }

    const value = this.switchForm.getRawValue();
    const body: AbstractSwitch = {
      description: value.description,
      ip: value.ip,
    };

    if (value.community !== "") {
      body.community = value.community;
    }

    this.saving = true;
    try {
      await firstValueFrom(
        this.switchService
          .switchIdPut(this.switchId, body)
          .pipe(takeUntilDestroyed(this.destroyRef)),
      );
      if (this.destroyRef.destroyed) return;
      this.notificationService.successNotification(
        $localize`:@@switch.edit.saved:Commutateur modifié`,
      );
      void this.router.navigate(["/switch", this.switchId, "admin"]);
    } catch (error) {
      if (!this.destroyRef.destroyed) {
        this.notifyError(
          error,
          $localize`:@@switch.edit.save-error:Impossible de modifier le commutateur.`,
        );
      }
    } finally {
      this.saving = false;
    }
  }

  async deleteSwitch(): Promise<void> {
    if (this.switchId === null || this.saving || this.deleting) return;

    this.deleting = true;
    try {
      const confirmed = await this.dialogService.confirm({
        title: $localize`:@@switch.delete.title:Supprimer le commutateur`,
        text: $localize`:@@switch.delete.confirm:Voulez-vous vraiment supprimer ce commutateur ? Cette action est irréversible.`,
        confirmText: $localize`:@@common.delete:Supprimer`,
        danger: true,
      });
      if (!confirmed || this.destroyRef.destroyed) return;

      await firstValueFrom(
        this.switchService
          .switchIdDelete(this.switchId)
          .pipe(takeUntilDestroyed(this.destroyRef)),
      );
      if (this.destroyRef.destroyed) return;
      this.notificationService.successNotification(
        $localize`:@@switch.deleted:Commutateur supprimé`,
      );
      void this.router.navigate(["/switch/search"]);
    } catch (error) {
      if (!this.destroyRef.destroyed) {
        this.notifyError(
          error,
          $localize`:@@switch.delete.error:Impossible de supprimer le commutateur.`,
        );
      }
    } finally {
      this.deleting = false;
    }
  }

  private notifyError(error: unknown, message: string): void {
    this.notificationService.errorNotification(
      error instanceof HttpErrorResponse ? error.status : 500,
      undefined,
      message,
    );
  }
}
