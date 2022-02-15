import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { first, map, Observable } from 'rxjs';
import Swal from 'sweetalert2';
import { Device, DeviceService } from '../../../api';

@Component({
  selector: 'app-element',
  templateUrl: './element.component.html',
  styleUrls: ['./element.component.sass']
})
export class ElementComponent implements OnInit {
  @Input() device: Device | undefined;
  @Input() macHighlighted: Observable<string>;
  @Output() removed: EventEmitter<Device> = new EventEmitter<Device>();

  mab$: Observable<boolean>;
  isCollapse: boolean = true;

  constructor(
    private deviceService: DeviceService,
  ) { }

  ngOnInit(): void {
    if (this.device == undefined) {
      throw new Error("device undefined");
    }
    this.refreshMAB();
  }

  public deviceDelete(deviceId: number) {
    this.deviceService.deviceDeviceIdDelete(deviceId)
      .pipe(
        first(),
        map(() => {
          return null; // @TODO return the device ?
        }),
        first(),
      )
      .subscribe(() => {
        this.removed.emit(this.device);
      });
  }

  public toogleDeviceDetails(): void {
    this.isCollapse = !this.isCollapse;
  }

  private refreshMAB(): void {
    this.mab$ = this.deviceService.deviceMabGet(this.device.id);
  }

  public updateMAB(): void {
    Swal.fire({
      title: "Changer le MAB",
      text: "Voulez-vous changer le MAB pour l'appareil avec la MAC: " + this.device.mac,
      icon: "warning",
      showCancelButton: true,
    }).then((result) => {
      if (result.isConfirmed) {
        this.deviceService.deviceMabPut(this.device.id)
          .subscribe((_) => {
            this.refreshMAB();
          });
      }
    });
  }
}
