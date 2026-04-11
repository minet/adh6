import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from "@angular/core";
import {BehaviorSubject, first, Observable, of, shareReplay, switchMap, map} from "rxjs";
import Swal from "sweetalert2";
import {AbstractDevice, DeviceService, Device} from "../../../api";
import {CommonModule, AsyncPipe} from "@angular/common";
import {AblePipe} from "@casl/angular";

@Component({
  imports: [CommonModule, AsyncPipe, AblePipe],
  selector: "app-element",
  templateUrl: "./element.component.html",
})
export class ElementComponent implements OnInit, OnChanges {
  @Input() device!: Device;
  @Output() removed: EventEmitter<number> = new EventEmitter<number>();

  public device$!: Observable<AbstractDevice>;
  public vendor$!: Observable<string | null>;
  public mab$!: Observable<boolean>;
  public isCollapse = true;

  private readonly refreshTrigger$ = new BehaviorSubject<void>(undefined);

  constructor(private readonly deviceService: DeviceService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['device'] && !changes['device'].firstChange) {
      this.refreshDevice();
    }
  }

  private initObservables() {
    this.device$ = this.refreshTrigger$.pipe(
      switchMap((_, index) => {
        if (index === 0) return of(this.device as AbstractDevice);
        return this.deviceService.deviceIdGet(this.device.id!);
      }),
      shareReplay(1)
    );

    this.vendor$ = this.device$.pipe(
      map((device: AbstractDevice) => device.vendor || null)
    );

    this.mab$ = this.device$.pipe(
      map((device: AbstractDevice) => device.mab ?? false)
    );
  }

  ngOnInit(): void {
    if (!this.device) {
      throw new Error("device undefined");
    }
    this.initObservables();
  }

  private refreshDevice(): void {
    this.refreshTrigger$.next();
  }

  public deviceDelete() {
    this.deviceService
      .deviceIdDelete(this.device.id!)
      .pipe(first())
      .subscribe(() => {
        this.removed.emit(this.device.id);
      });
  }

  public toogleDeviceDetails(): void {
    this.isCollapse = !this.isCollapse;
  }

  public updateMAB(): void {
    void Swal.fire({
      title: "Changer le MAB",
      text: "Voulez-vous changer le MAB pour l'appareil ?",
      icon: "warning",
      showCancelButton: true,
    }).then((result: {isConfirmed: boolean}) => {
      if (result.isConfirmed) {
        this.deviceService.deviceIdMabPost(this.device.id!).subscribe(() => {
          this.refreshDevice();
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
            .deviceIdNamePut(this.device.id!, {name: result.value})
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
          .deviceIdWifiPasswordPost(this.device.id!)
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
          .deviceIdWifiPasswordDelete(this.device.id!)
          .pipe(first())
          .subscribe(() => this.refreshDevice());
      }
    });
  }
}
