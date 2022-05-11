import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Device, DeviceService } from '../../api';
import { takeWhile } from 'rxjs/operators';
import { LOCALE_ID, Inject } from '@angular/core';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-device-new',
  templateUrl: './new.component.html',
  styleUrls: ['./new.component.sass']
})
export class NewComponent {
  deviceForm: FormGroup;
  private alive = true;

  @Input() member_id: number;
  @Output() added: EventEmitter<Device> = new EventEmitter<Device>();

  constructor(
    private fb: FormBuilder,
    private deviceService: DeviceService,
    private notificationService: NotificationService,
    @Inject(LOCALE_ID) public locale: string) {
    this.createForm();
  }

  onSubmit() {
    const v = this.deviceForm.value;
    const device: Device = {
      mac: v.mac,
      connectionType: v.connectionType
    };

    if (this.member_id != null) {
      device.member = this.member_id;
    }

    this.deviceService.devicePost(device)
      .pipe(takeWhile(() => this.alive))
      .subscribe((res) => {
        this.notificationService.successNotification();
        this.added.emit(res);
      });
  }

  createForm() {
    this.deviceForm = this.fb.group({
      mac: ['', [Validators.required, Validators.pattern('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')]],
      connectionType: ['', [Validators.required, Validators.pattern('wired|wireless')]],
    });
  }

}
