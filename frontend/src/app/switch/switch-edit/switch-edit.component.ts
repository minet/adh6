import {Component} from "@angular/core";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  AbstractControl,
} from "@angular/forms";
import {SwitchService} from "../../api";

@Component({
  selector: "app-switch-edit",
  templateUrl: "./switch-edit.component.html",
  styleUrls: ["./switch-edit.component.css"],
})
export class SwitchEditComponent {
  switchForm: UntypedFormGroup;

  constructor(
    private readonly fb: UntypedFormBuilder,
    public switchService: SwitchService,
  ) {
    this.switchForm = this.fb.group({
      ip: [
        "",
        [
          Validators.required.bind(Validators),
          Validators.minLength(11).bind(Validators),
          Validators.maxLength(15).bind(Validators),
        ],
      ],
    });
  }
}
