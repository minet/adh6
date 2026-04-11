import {Router} from "@angular/router";
import {Component, OnInit} from "@angular/core";
import {Observable} from "rxjs";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
  FormsModule,
} from "@angular/forms";
import {AbstractSwitch, Switch, SwitchService, DiscoveredPort, PortService, AbstractPort} from "../../api";
import {finalize, takeWhile} from "rxjs/operators";
import {NotificationService} from "../../notification.service";
import {CommonModule} from "@angular/common";

@Component({
  imports: [ReactiveFormsModule, CommonModule, FormsModule],
  selector: "app-switch-new",
  templateUrl: "./switch-new.component.html",
  styleUrls: ["./switch-new.component.css"],
  standalone: true,
})
export class SwitchNewComponent implements OnInit {
  switchForm: UntypedFormGroup;
  disabled = false;
  step = 1;
  createdSwitchId?: number;
  discoveredPorts: (DiscoveredPort & {selected: boolean})[] = [];
  discovering = false;
  addingPorts = false;

  constructor(
    private readonly fb: UntypedFormBuilder,
    public switchService: SwitchService,
    public portService: PortService,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
  ) {
    this.switchForm = this.fb.group({
      ip: [
        "",
        [
          Validators.required,
          Validators.pattern(/^(\d{1,3}\.){3}\d{1,3}$/),
        ],
      ],
      description: ["", Validators.required],
      community: ["", Validators.required],
    });
  }

  ngOnInit(): void {}

  onSubmitSwitch() {
    this.disabled = true;
    const v = this.switchForm.value;
    const varSwitch: Switch = {
      description: v.description,
      ip: v.ip,
      community: v.community,
    };

    this.switchService
      .switchPost(varSwitch)
      .pipe(finalize(() => this.disabled = false))
      .subscribe({
        next: (created) => {
          this.createdSwitchId = created.id;
          this.step = 2;
          this.discoverPorts();
        },
        error: (err: {status: number}) => this.notificationService.errorNotification(err.status)
      });
  }

  discoverPorts() {
    if (!this.createdSwitchId) return;
    this.discovering = true;
    this.switchService.switchIdDiscoverPortsGet(this.createdSwitchId)
      .pipe(finalize(() => this.discovering = false))
      .subscribe({
        next: (ports) => {
          this.discoveredPorts = ports.map(p => ({...p, selected: true}));
        },
        error: (err: {status: number}) => this.notificationService.errorNotification(err.status)
      });
  }

  addSelectedPorts() {
    if (!this.createdSwitchId) return;
    const selected = this.discoveredPorts.filter(p => p.selected);
    if (selected.length === 0) {
      void this.router.navigate(["/switch", this.createdSwitchId, "view"]);
      return;
    }

    const portsToAdd: AbstractPort[] = selected.map(p => ({
      switchObj: this.createdSwitchId!,
      portNumber: p.portNumber,
      oid: p.oid,
      room: null as any // Room will be assigned later
    }));

    this.addingPorts = true;
    this.portService.portBulkPost(portsToAdd)
      .pipe(finalize(() => this.addingPorts = false))
      .subscribe({
        next: (result) => {
          this.notificationService.successNotification(
            `Ports ajoutés : ${result.success} succès, ${result.failed} échec(s)`
          );
          void this.router.navigate(["/switch", this.createdSwitchId, "view"]);
        },
        error: (err: {status: number}) => this.notificationService.errorNotification(err.status)
      });
  }

  toggleAll(event: any) {
    const checked = event.target.checked;
    this.discoveredPorts.forEach(p => p.selected = checked);
  }
}
