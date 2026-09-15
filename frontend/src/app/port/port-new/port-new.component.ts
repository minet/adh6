import {ActivatedRoute, Router} from "@angular/router";
import {Component, OnInit} from "@angular/core";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
} from "@angular/forms";
import {Port, PortService} from "../../api";
import {takeWhile} from "rxjs/operators";
import {NotificationService} from "../../notification.service";
import {RoomSelectComponent} from "../../ui/room-select.component";

interface PortForm {
  portNumber: FormControl<number>;
  roomNumber: FormControl<number | null>;
}

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, RoomSelectComponent],
  selector: "app-port-new",
  template: `
    <h1 class="title is-1" i18n="@@port.new.title">Création d'un port</h1>
    <form [formGroup]="portForm" (ngSubmit)="onSubmit()" novalidate>
      <div class="field">
        <label i18n="@@port.new.port-number">Numéro du port</label>
        <input
          class="input is-fullwidth"
          formControlName="portNumber"
          type="text" />
      </div>
      <div class="field">
        <label i18n="@@room.form.room-number">Numéro de chambre</label>
        <app-room-select formControlName="roomNumber" valueField="id" />
      </div>
      <div class="field">
        <button
          type="submit"
          [disabled]="portForm.status === 'INVALID'"
          class="button is-primary is-fullwidth"
          i18n="@@common.create">
          Créer
        </button>
      </div>
    </form>
  `,
})
export class PortNewComponent implements OnInit {
  portForm: FormGroup<PortForm>;
  switch_id: number;
  private readonly alive = true;

  constructor(
    private readonly fb: FormBuilder,
    public portService: PortService,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
    private readonly route: ActivatedRoute,
  ) {
    this.createForm();
  }

  createForm() {
    this.portForm = this.fb.group({
      roomNumber: new FormControl<number | null>(null, Validators.required),
      portNumber: [0, [Validators.required]],
    });
  }

  onSubmit() {
    if (this.portForm.invalid) {
      return;
    }
    const v = this.portForm.value;
    const port = {
      portNumber: "" + v.portNumber,
      room: +v.roomNumber!,
      switchObj: this.switch_id,
    };

    this.portService
      .portPost(port)
      .pipe(takeWhile(() => this.alive))
      .subscribe((res: Port) => {
        void this.router.navigate(["/port", this.switch_id, res.id]);
        this.notificationService.successNotification();
      });
  }

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.switch_id = +params["switch_id"];
    });
  }
}
