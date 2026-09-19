import {Location} from "@angular/common";
import {PureAbility} from "@casl/ability";
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
import {Observable} from "rxjs";
import {finalize} from "rxjs/operators";
import {MemberService, PasswordPolicyRule} from "../api";
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
export class MemberPasswordEditComponent implements OnInit {
  disabled = false;
  readonly isAdmin: boolean;
  readonly passwordForm: UntypedFormGroup;
  passwordPolicy: PasswordPolicyRule[] | null = null;
  passwordPolicyLoadFailed = false;
  passwordPolicyLoading = false;

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

  ngOnInit(): void {
    if (!this.isAdmin) return;

    this.passwordPolicyLoading = true;
    this.memberService
      .memberPasswordPolicyGet()
      .pipe(finalize(() => (this.passwordPolicyLoading = false)))
      .subscribe({
        next: (policy) => (this.passwordPolicy = policy),
        error: () => (this.passwordPolicyLoadFailed = true),
      });
  }

  passwordPolicyDescription(rule: PasswordPolicyRule): string {
    const defaultValues: Record<string, string> = {
      digits: "1",
      length: "8",
      lowerCase: "1",
      maxLength: "64",
      specialChars: "1",
      upperCase: "1",
    };
    const value = rule.value || defaultValues[rule.name] || "";

    switch (rule.name) {
      case "length":
        return $localize`:@@password.policy.min-length:Au moins ${value}:count: caractères.`;
      case "maxLength":
        return $localize`:@@password.policy.max-length:Au maximum ${value}:count: caractères.`;
      case "digits":
        return $localize`:@@password.policy.digits:Au moins ${value}:count: chiffres.`;
      case "lowerCase":
        return $localize`:@@password.policy.lowercase:Au moins ${value}:count: lettres minuscules.`;
      case "upperCase":
        return $localize`:@@password.policy.uppercase:Au moins ${value}:count: lettres majuscules.`;
      case "specialChars":
        return $localize`:@@password.policy.special-chars:Au moins ${value}:count: caractères spéciaux.`;
      case "notUsername":
        return $localize`:@@password.policy.not-username:Ne doit pas être identique au nom d’utilisateur.`;
      case "notContainsUsername":
        return $localize`:@@password.policy.not-contains-username:Ne doit pas contenir le nom d’utilisateur.`;
      case "notEmail":
        return $localize`:@@password.policy.not-email:Ne doit pas être identique à l’adresse e-mail.`;
      case "regexPattern":
        return $localize`:@@password.policy.regex:Doit respecter l’expression régulière suivante : ${value}:pattern:.`;
      case "passwordHistory":
        return $localize`:@@password.policy.history:Ne doit pas faire partie des ${value}:count: derniers mots de passe.`;
      case "passwordHistoryDays":
        return $localize`:@@password.policy.history-days:Ne doit pas avoir été utilisé durant les ${value}:count: derniers jours.`;
      case "passwordBlacklist":
        return $localize`:@@password.policy.blacklist:Ne doit pas figurer dans la liste des mots de passe interdits.`;
      case "forceExpiredPasswordChange":
        return $localize`:@@password.policy.expiration:Devra être changé après ${value}:count: jours.`;
      default:
        return rule.value
          ? $localize`:@@password.policy.additional-with-value:Règle Keycloak supplémentaire « ${rule.name}:name: » : ${rule.value}:value:.`
          : $localize`:@@password.policy.additional:Règle Keycloak supplémentaire « ${rule.name}:name: ».`;
    }
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
