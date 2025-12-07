import {Router} from "@angular/router";
import {Component} from "@angular/core";
import {Observable} from "rxjs";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import {AbstractSwitch, Switch, SwitchService} from "../../api";
import {takeWhile} from "rxjs/operators";
import {NotificationService} from "../../notification.service";

@Component({
  imports: [ReactiveFormsModule],
  selector: "app-switch-new",
  templateUrl: "./switch-new.component.html",
  styleUrls: ["./switch-new.component.css"],
  standalone: true,
})
export class SwitchNewComponent {
  switches$: Observable<AbstractSwitch[]>;
  switchForm: UntypedFormGroup;
  disabled = false;
  private readonly alive = true;

  constructor(
    private readonly fb: UntypedFormBuilder,
    public switchService: SwitchService,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
  ) {
    this.switchForm = this.fb.group({
      ip: [
        "",
        [
          Validators.required,
          Validators.minLength(11),
          Validators.maxLength(15),
        ],
      ],
      description: ["", Validators.required],
      community: ["", Validators.required],
    });
    this.switches$ = this.switchService.switchGet();
  }

  onSubmit() {
    const v = this.switchForm.value;
    const varSwitch: Switch = {
      description: v.description,
      ip: v.ip,
      community: v.community,
    };

    this.switchService
      .switchPost(varSwitch)
      .pipe(takeWhile(() => this.alive))
      .subscribe(() => {
        void this.router.navigate(["/switch/search"]);
        this.notificationService.successNotification();
      });
  }
}
