import {Component, EventEmitter, Input, OnInit, Output} from "@angular/core";
import {BehaviorSubject, first, Observable, of, shareReplay, switchMap} from "rxjs";
import Swal from "sweetalert2";
import {AbstractDevice, DeviceService} from "../../../api";
import {CommonModule, AsyncPipe} from "@angular/common";
import {AblePipe} from "@casl/angular";

@Component({
  imports: [CommonModule, AsyncPipe, AblePipe],
  selector: "app-element",
  templateUrl: "./element.component.html",
})
export class ElementComponent implements OnInit {
  @Input() deviceId!: number;
  @Output() removed: EventEmitter<number> = new EventEmitter<number>();

  public device$!: Observable<AbstractDevice>;
  public vendor$!: Observable<string | null>;
  public mab$!: Observable<boolean>;
  public isCollapse = true;

  private readonly refreshTrigger$ = new BehaviorSubject<void>(undefined);

  constructor(private readonly deviceService: DeviceService) {}

  ngOnInit(): void {
    if (this.deviceId == undefined) {
      throw new Error("device undefined");
    }
    this.refreshMAB();
    this.device$ = this.refreshTrigger$.pipe(
      switchMap(() => this.deviceService.deviceIdGet(this.deviceId)),
      shareReplay(1),
    );
    this.vendor$ = this.device$.pipe(
      switchMap((device: AbstractDevice) =>
        device.name
          ? of(null)
          : this.deviceService.deviceIdVendorGet(this.deviceId),
      ),
    );
  }

  private refreshDevice(): void {
    this.refreshTrigger$.next();
  }

  public deviceDelete() {
    this.deviceService
      .deviceIdDelete(this.deviceId)
      .pipe(first())
      .subscribe(() => {
        this.removed.emit(this.deviceId);
      });
  }

  public toogleDeviceDetails(): void {
    this.isCollapse = !this.isCollapse;
  }

  private refreshMAB(): void {
    this.mab$ = this.deviceService.deviceIdMabGet(this.deviceId);
  }

  public updateMAB(): void {
    void Swal.fire({
      title: "Changer le MAB",
      text: "Voulez-vous changer le MAB pour l'appareil ?",
      icon: "warning",
      showCancelButton: true,
    }).then((result: {isConfirmed: boolean}) => {
      if (result.isConfirmed) {
        this.deviceService.deviceIdMabPost(this.deviceId).subscribe(() => {
          this.refreshMAB();
        });
      }
    });
  }

  public rename(): void {
    this.device$.pipe(first()).subscribe((device: AbstractDevice) => {
      void Swal.fire({
        title: "Renommer l'appareil",
        input: "text",
        inputValue: device.name ?? "",
        inputPlaceholder: "Nom de l'appareil",
        showCancelButton: true,
        cancelButtonText: "Annuler",
        confirmButtonText: "Renommer",
      }).then((result: {isConfirmed: boolean; value?: string}) => {
        if (result.isConfirmed && result.value !== undefined) {
          this.deviceService
            .deviceIdNamePut(this.deviceId, {name: result.value})
            .pipe(first())
            .subscribe(() => this.refreshDevice());
        }
      });
    });
  }

  public generateWifiPassword(): void {
    void Swal.fire({
      title: "Générer un mot de passe WiFi",
      text: "Un nouveau mot de passe WiFi sera généré pour cet appareil.",
      icon: "question",
      showCancelButton: true,
      cancelButtonText: "Annuler",
      confirmButtonText: "Générer",
    }).then((result: {isConfirmed: boolean}) => {
      if (result.isConfirmed) {
        this.deviceService
          .deviceIdWifiPasswordPost(this.deviceId)
          .pipe(first())
          .subscribe(() => this.refreshDevice());
      }
    });
  }

  public clearWifiPassword(): void {
    void Swal.fire({
      title: "Supprimer le mot de passe WiFi",
      text: "Le mot de passe WiFi de cet appareil sera supprimé.",
      icon: "warning",
      showCancelButton: true,
      cancelButtonText: "Annuler",
      confirmButtonText: "Supprimer",
    }).then((result: {isConfirmed: boolean}) => {
      if (result.isConfirmed) {
        this.deviceService
          .deviceIdWifiPasswordDelete(this.deviceId)
          .pipe(first())
          .subscribe(() => this.refreshDevice());
      }
    });
  }
}
