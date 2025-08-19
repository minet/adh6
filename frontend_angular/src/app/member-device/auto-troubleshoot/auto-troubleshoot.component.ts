import {Component, Input, OnInit} from "@angular/core";
import {Observable} from "rxjs";
import {Member, MemberService, MemberStatus} from "../../api";
import {CommonModule, AsyncPipe, DatePipe} from "@angular/common";

@Component({
  imports: [CommonModule, AsyncPipe, DatePipe],
  selector: "app-auto-troubleshoot",
  template: `
    @if (statuses$ | async; as statuses) {
      @if (statuses.length > 0) {
        <div class="alert alert-danger mt-4">
          <h4 i18n="dashboard auto troubleshoot">Dépannage automatique</h4>
          <ul class="text-left">
            @for (status of statuses; track status) {
              <li>
                @if (status.status === "LOGIN_INCORRECT_WRONG_PASSWORD") {
                  <ng-container i18n="login incorrect wrong password"
                    >Mot de passe incorrect pour l'appareil
                    <code>{{ status.comment }}</code> ({{
                      status.lastTimestamp | date: "short"
                    }})</ng-container
                  >
                }
                @if (status.status === "LOGIN_INCORRECT_WRONG_MAC") {
                  <ng-container i18n="login incorrect wrong mac"
                    >Vous avez essayé de vous connecter avec l'appareil
                    <code>{{ status.comment }}</code
                    >, mais cet appareil n'est pas ajouté à votre compte ({{
                      status.lastTimestamp | date: "short"
                    }})</ng-container
                  >
                }
                @if (status.status === "LOGIN_INCORRECT_WRONG_USER") {
                  <ng-container i18n="login incorrect wrong user"
                    >Vous avez essayé de vous connecter avec votre appareil
                    <code>{{ status.comment }}</code> mais depuis un autre
                    compte ({{
                      status.lastTimestamp | date: "short"
                    }})</ng-container
                  >
                }
                @if (status.status === "LOGIN_INCORRECT_SSL_ERROR") {
                  <ng-container i18n="login incorrect ssl error"
                    >L'appareil <code>{{ status.comment }}</code> est mal
                    configuré, vérifiez la configuration via les tutoriels, en
                    particulier la présence de MSCHAPv2 et la non-validation du
                    certificat ({{
                      status.lastTimestamp | date: "short"
                    }})</ng-container
                  >
                }
              </li>
            }
          </ul>
        </div>
      }
    }
  `,
})
export class AutoTroubleshootComponent implements OnInit {
  statuses$: Observable<MemberStatus[]>;

  @Input() member: Member;

  constructor(private memberService: MemberService) {}

  ngOnInit(): void {
    this.statuses$ = this.memberService.memberIdStatusesGet(
      this.member.id,
      "body",
    );
  }
}
