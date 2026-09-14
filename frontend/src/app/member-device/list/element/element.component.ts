import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
} from "@angular/core";
import {
  BehaviorSubject,
  first,
  Observable,
  of,
  shareReplay,
  switchMap,
  map,
} from "rxjs";
import {AbstractDevice, DeviceService, Device} from "../../../api";
import {CommonModule, AsyncPipe} from "@angular/common";
import {DialogService} from "../../../ui/dialog.service";

@Component({
  imports: [CommonModule, AsyncPipe],
  selector: "app-element",
  templateUrl: "./element.component.html",
})
export class ElementComponent implements OnInit, OnChanges {
  @Input() device!: Device;
  @Output() removed: EventEmitter<number> = new EventEmitter<number>();

  public device$!: Observable<AbstractDevice>;
  public vendor$!: Observable<string | null>;
  public isCollapse = true;

  private readonly refreshTrigger$ = new BehaviorSubject<void>(undefined);

  constructor(
    private readonly deviceService: DeviceService,
    private readonly dialogService: DialogService,
  ) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes["device"] && !changes["device"].firstChange) {
      this.refreshDevice();
    }
  }

  private initObservables() {
    this.device$ = this.refreshTrigger$.pipe(
      switchMap((_, index) => {
        if (index === 0) return of(this.device as AbstractDevice);
        return this.deviceService.deviceIdGet(this.device.id!);
      }),
      shareReplay(1),
    );

    this.vendor$ = this.device$.pipe(
      map((device: AbstractDevice) => device.vendor || null),
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

  public rename(): void {
    this.device$.pipe(first()).subscribe((device: AbstractDevice) => {
      void this.dialogService
        .prompt({
          title: "Renommer l'appareil",
          value: device.name ?? "",
          placeholder: "Nom de l'appareil",
          confirmText: "Renommer",
        })
        .then((name) => {
          if (name === null) return;
          this.deviceService
            .deviceIdNamePut(this.device.id!, {name})
            .pipe(first())
            .subscribe(() => this.refreshDevice());
        });
    });
  }

  public generateWifiPassword(): void {
    void this.dialogService
      .confirm({
        title: "Générer un mot de passe WiFi",
        text: "Un nouveau mot de passe WiFi sera généré pour cet appareil.",
        confirmText: "Générer",
      })
      .then((confirmed) => {
        if (!confirmed) return;
        this.deviceService
          .deviceIdWifiPasswordPost(this.device.id!)
          .pipe(first())
          .subscribe(() => this.refreshDevice());
      });
  }

  public clearWifiPassword(): void {
    void this.dialogService
      .confirm({
        title: "Supprimer le mot de passe WiFi",
        text: "Le mot de passe WiFi de cet appareil sera supprimé.",
        confirmText: "Supprimer",
        danger: true,
      })
      .then((confirmed) => {
        if (!confirmed) return;
        this.deviceService
          .deviceIdWifiPasswordDelete(this.device.id!)
          .pipe(first())
          .subscribe(() => this.refreshDevice());
      });
  }
}
