import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {Device, DeviceService, Member, Port} from '../api';
import {NotificationsService} from 'angular2-notifications';
import {takeWhile} from 'rxjs/operators';

@Component({
  selector: 'app-device-new',
  templateUrl: './device-new.component.html',
  styleUrls: ['./device-new.component.sass']
})
export class DeviceNewComponent implements OnInit {
  deviceForm: FormGroup;
  private alive = true;

  @Input() member_id: number;
  @Output() added: EventEmitter<Device> = new EventEmitter<Device>();

  constructor(
    private fb: FormBuilder,
    private deviceService: DeviceService,
    private notif: NotificationsService,
  ) {
    this.createForm();
  }

  ngOnInit(): void {
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
        this.notif.success('Success');
        this.added.emit(res);
      });
  }

  createForm() {
    this.deviceForm = this.fb.group({
      mac: ['', [Validators.required, Validators.pattern('^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$')]],
      connectionType: ['', [Validators.required, Validators.pattern('wired|wireless')]],
    });
  }

}
