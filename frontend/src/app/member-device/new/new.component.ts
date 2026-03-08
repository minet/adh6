import {Component, EventEmitter, Input, Output} from "@angular/core";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import {AbstractDevice, DeviceBody, DeviceService} from "../../api";
import {takeWhile} from "rxjs/operators";
import {LOCALE_ID, Inject} from "@angular/core";
import {NotificationService} from "../../notification.service";
import {CommonModule} from "@angular/common";
import {MacAddressFormatterDirective} from "../../shared/directives/mac-address-formatter.directive";

@Component({
  selector: "app-device-new",
  templateUrl: "./new.component.html",
  styleUrls: ["./new.component.css"],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MacAddressFormatterDirective],
})
export class NewComponent {
  deviceForm!: UntypedFormGroup;
  private readonly alive = true;

  @Input() member_id!: number;
  @Output() added: EventEmitter<AbstractDevice> =
    new EventEmitter<AbstractDevice>();

  constructor(
    private readonly fb: UntypedFormBuilder,
    private readonly deviceService: DeviceService,
    private readonly notificationService: NotificationService,
    @Inject(LOCALE_ID) public locale: string,
  ) {
    this.createForm();
  }

  onSubmit() {
    const v = this.deviceForm.value;
    const device: DeviceBody = {
      mac: v.mac as string,
      connectionType: v.connectionType as DeviceBody.ConnectionTypeEnum,
      member: this.member_id,
    };

    this.deviceService
      .devicePost(device)
      .pipe(takeWhile(() => this.alive))
      .subscribe({
        next: (res) => {
          this.notificationService.successNotification();
          this.deviceService.deviceIdGet(res).subscribe((d) => {
            this.added.emit(d);
          });
        },
        error: (err) => {
          const detail: string = err?.error?.detail ?? "";
          if (
            detail.includes("room for member") &&
            detail.includes("was not found")
          ) {
            this.notificationService.errorNotification(
              404,
              "Pas de chambre",
              "Ce membre n'a pas de numéro de chambre assigné.",
            );
          } else {
            this.notificationService.errorNotification(err?.status ?? 500);
          }
        },
      });
  }

  createForm() {
    this.deviceForm = this.fb.group({
      mac: [
        "",
        [
          Validators.required,
          Validators.pattern("^([0-9A-Fa-f]{2}[-:]){5}([0-9A-Fa-f]{2})$"),
        ],
      ],
      connectionType: [
        "",
        [Validators.required, Validators.pattern("wired|wireless")],
      ],
    });
  }
}
