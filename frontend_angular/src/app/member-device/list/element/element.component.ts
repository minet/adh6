import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { first, map, Observable, shareReplay } from 'rxjs';
import Swal from 'sweetalert2';
import { AbstractDevice, DeviceService } from '../../../api';

@Component({
  selector: 'app-element',
  templateUrl: './element.component.html',
  styleUrls: ['./element.component.sass']
})
export class ElementComponent implements OnInit {
  @Input() deviceId: number;
  @Output() removed: EventEmitter<number> = new EventEmitter();

  public device$: Observable<AbstractDevice>;
  public vendor$: Observable<string>;
  public mab$: Observable<boolean>;
  public isCollapse: boolean = true;

  constructor(
    private deviceService: DeviceService,
  ) { }

  ngOnInit(): void {
    if (this.deviceId == undefined) {
      throw new Error("device undefined");
    }
    this.refreshMAB();
    this.device$ = this.deviceService.deviceIdGet(this.deviceId).pipe(shareReplay(1));
    this.vendor$ = this.deviceService.deviceIdVendorGet(this.deviceId).pipe(shareReplay(1));
  }

  public deviceDelete() {
    this.deviceService.deviceIdDelete(this.deviceId)
      .pipe(
        first(),
        map(() => {
          return null;
        }),
        first(),
      )
      .subscribe(() => {
        this.removed.emit(this.deviceId);
      }).unsubscribe();
  }

  public toogleDeviceDetails(): void {
    this.isCollapse = !this.isCollapse;
  }

  private refreshMAB(): void {
    this.mab$ = this.deviceService.deviceIdMabGet(this.deviceId);
  }

  public updateMAB(): void {
    Swal.fire({
      title: "Changer le MAB",
      text: "Voulez-vous changer le MAB pour l'appareil ?",
      icon: "warning",
      showCancelButton: true,
    }).then((result) => {
      if (result.isConfirmed) {
        this.deviceService.deviceIdMabPost(this.deviceId)
          .subscribe((_) => {
            this.refreshMAB();
          }).unsubscribe();
      }
    });
  }
}
