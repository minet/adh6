import {Component, OnInit} from "@angular/core";
import {
  AbstractControl,
  ReactiveFormsModule,
  UntypedFormBuilder,
  UntypedFormGroup,
  ValidationErrors,
  Validators,
} from "@angular/forms";
import {ActivatedRoute, Router} from "@angular/router";
import {finalize, map} from "rxjs/operators";
import {MemberService} from "../api";
import {CommonModule, Location} from "@angular/common";
import {NotificationService} from "../notification.service";

function passwordConfirming(c: AbstractControl): ValidationErrors | null {
  if (!c || !c.value) {
    return;
  }
  const pwd = c.value["password"];
  const cpwd = c.value["password_confirm"];

  if (!pwd || !cpwd) {
    return;
  }
  if (pwd !== cpwd) {
    return {invalid: true};
  }
}

@Component({
  imports: [CommonModule, ReactiveFormsModule],
  selector: "app-member-password-edit",
  templateUrl: "./member-password-edit.component.html",
})
export class MemberPasswordEditComponent implements OnInit {
  public showPassword: boolean = false;
  public showConfirmPassword: boolean = false;

  constructor(
    private fb: UntypedFormBuilder,
    private notificationService: NotificationService,
    private router: Router,
    private route: ActivatedRoute,
    private memberService: MemberService,
    private location: Location,
  ) {}

  disabled = false;
  memberPassword: UntypedFormGroup;

  /*
  Taken from https://stackoverflow.com/a/37597001
   */
  strEncodeUTF16(str: string) {
    const buf = new ArrayBuffer(str.length * 2);
    const bufView = new Uint16Array(buf);
    for (let i = 0, strLen = str.length; i < strLen; i++) {
      bufView.set([str.charCodeAt(i)], i);
    }
    return bufView;
  }

  ngOnInit() {
    this.createForm();
  }

  createForm(): void {
    // These checks or run on the frontend to give instant feedback to the user and on the backend as a HTTP request could be sent with an invalid password.
    // nosemgrep: ajinabraham.njsscan.generic.hardcoded_secrets.node_password
    const passwordValidationRegex: string =
      "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[\"'#!@$%^&(){}[\\]:;<>,.*?/~_+\-=|]).*$"; // Regex pattern to ensure at least one uppercase letter, one lowercase letter, one digit, and one special character
    /***
     * ^ - Start of string
     * (?=.*[!@#$%^&*]) - At least one special character from the set !@#$%^&*
     * (?=.*\d) - At least one digit
     * (?=.*[a-z]) - At least one lowercase letter
     * (?=.*[A-Z]) - At least one uppercase letter
     * .* - Any character (except for line terminators) zero or more times
     * $ - End of string
     */
    this.memberPassword = this.fb.group(
      {
        password: [
          "",
          [
            Validators.required,
            Validators.minLength(8),
            Validators.maxLength(64),
            Validators.pattern(passwordValidationRegex),
          ],
        ],
        password_confirm: ["", [Validators.required]],
      },
      {
        validator: passwordConfirming,
      },
    );
  }

  changePassword(): void {
    const password: string = this.memberPassword.value.password;
    this.route.paramMap
      .pipe(
        map((params) => {
          const member_id = +params.get("member_id");
          console.log(+params.get("creation") === 1);
          this.updatePasswordOfUser(
            member_id,
            password,
            +params.get("creation") === 1,
          );
        }),
        finalize(() => (this.disabled = false)), // danura 07/08/2025 does nothing as this.disabled is never set to true
      )
      .subscribe((_) => {});
  }

  private updatePasswordOfUser(
    member_id: number,
    PasswordVar: string,
    creation: boolean,
  ) {
    return this.memberService
      .memberIdPasswordPut(+member_id, {password: PasswordVar}, "response")
      .subscribe((_) => {
        this.notificationService.successNotification();
        if (!creation) {
          this.location.back();
        } else {
          this.router.navigate(["/member/view", member_id]);
        }
      });
  }
}
