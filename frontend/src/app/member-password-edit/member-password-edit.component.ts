import {Location} from "@angular/common";
import {PureAbility} from "@casl/ability";
import {Component} from "@angular/core";
import {
  AbstractControl,
  ReactiveFormsModule,
  UntypedFormBuilder,
  UntypedFormGroup,
  ValidationErrors,
  Validators,
} from "@angular/forms";
import {ActivatedRoute, Router} from "@angular/router";
import {Observable} from "rxjs";
import {finalize} from "rxjs/operators";
import {MemberService} from "../api";
import {NotificationService} from "../notification.service";

function matchingPasswords(control: AbstractControl): ValidationErrors | null {
  const password = control.get("password")?.value as string | undefined;
  const confirmation = control.get("passwordConfirm")?.value as
    | string
    | undefined;
  return password && confirmation && password !== confirmation
    ? {passwordMismatch: true}
    : null;
}

@Component({
  imports: [ReactiveFormsModule],
  selector: "app-member-password-edit",
  templateUrl: "./member-password-edit.component.html",
})
export class MemberPasswordEditComponent {
  disabled = false;
  readonly isAdmin: boolean;
  readonly passwordForm: UntypedFormGroup;

  constructor(
    formBuilder: UntypedFormBuilder,
    ability: PureAbility,
    private readonly notificationService: NotificationService,
    private readonly router: Router,
    private readonly route: ActivatedRoute,
    private readonly memberService: MemberService,
    private readonly location: Location,
  ) {
    this.isAdmin = ability.can("manage", "admin");
    this.passwordForm = formBuilder.group(
      {
        password: ["", [Validators.required]],
        passwordConfirm: ["", [Validators.required]],
      },
      {validators: matchingPasswords},
    );
  }

  sendPasswordLink(): void {
    const memberId = this.memberId();
    if (memberId === null) return;
    this.runRequest(
      this.memberService.memberIdPasswordResetPost(memberId, "response"),
      $localize`:@@password.email.sent:Lien de définition du mot de passe envoyé`,
      memberId,
    );
  }

  setPassword(): void {
    const memberId = this.memberId();
    if (memberId === null || !this.isAdmin || this.passwordForm.invalid) return;
    const password = this.passwordForm.value.password as string;
    this.runRequest(
      this.memberService.memberIdPasswordPut(memberId, {password}, "response"),
      $localize`:@@password.updated:Mot de passe modifié`,
      memberId,
    );
  }

  private memberId(): number | null {
    const memberId = Number(this.route.snapshot.paramMap.get("member_id"));
    if (!Number.isInteger(memberId) || memberId <= 0) {
      this.notificationService.errorNotification(400);
      return null;
    }
    return memberId;
  }

  private runRequest(
    request: Observable<unknown>,
    successMessage: string,
    memberId: number,
  ): void {
    this.disabled = true;
    request.pipe(finalize(() => (this.disabled = false))).subscribe({
      next: () => {
        this.passwordForm.reset();
        this.notificationService.successNotification(successMessage);
        if (this.route.snapshot.paramMap.get("creation") === "1") {
          void this.router.navigate(["/member/view", memberId, "profile"]);
        } else {
          this.location.back();
        }
      },
      error: () => undefined,
    });
  }
}
