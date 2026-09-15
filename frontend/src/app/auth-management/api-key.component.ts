import {CommonModule} from "@angular/common";
import {Component, OnInit} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {Observable} from "rxjs";
import {ApiKey, ApiKeysPostRequest, AuthenticationService, Role} from "../api";
import {DialogService} from "../ui/dialog.service";

@Component({
  imports: [CommonModule, FormsModule],
  selector: "app-api-key",
  template: `
    <div class="level">
      <div class="level-item is-fullwidth mr-2">
        <input
          class="input"
          placeholder="Identifiant"
          i18n-placeholder="@@auth.login.placeholder"
          type="text"
          [(ngModel)]="login" />
      </div>
      <div class="level-right">
        <div class="level-item">
          <div class="select is-multiple">
            <select [(ngModel)]="roles" multiple size="3">
              <option value="0">Admin</option>
              <option value="1">Network</option>
              <option value="2" i18n="@@api-key.role.treasury">Trésorerie</option>
            </select>
          </div>
        </div>
        <div class="level-item">
          <button class="button is-primary" (click)="submit()" i18n="@@api-key.new">
            Nouvelle clef
          </button>
        </div>
      </div>
    </div>
    @if (result$ | async; as result) {
      <table class="table is-fullwidth">
        <thead>
          <tr>
            <th>Login</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @for (key of result; track key) {
            <tr>
              <td>{{ key.login }}</td>
              <td>
                <button class="button is-danger" (click)="delete(key.id)" i18n="@@common.delete">
                  Supprimer
                </button>
              </td>
            </tr>
          }
        </tbody>
      </table>
    } @else {
      <div class="notification is-info is-light has-text-centered">
        <h4 class="title is-4" i18n="@@common.loading.title">Chargement ...</h4>
      </div>
    }
  `,
})
export class ApiKeyComponent implements OnInit {
  public roleKeys = Object.values(Role);
  public result$!: Observable<ApiKey[]>;
  public login = "";
  public roles: string[] = [];

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly dialogService: DialogService,
  ) {}

  ngOnInit(): void {
    this.refreshApi();
  }

  public submit(): void {
    if (this.roles.length === 0 || this.login === "") {
      return;
    }

    const roles = [];
    for (let idx = 0; idx < this.roles.length; idx++) {
      if (idx === 0) {
        roles.push(Role.AdminWrite, Role.AdminRead);
      } else if (idx === 1) {
        roles.push(Role.NetworkWrite, Role.NetworkRead);
      } else if (idx === 2) {
        roles.push(Role.TreasurerWrite, Role.TreasurerRead);
      }
    }

    this.authenticationService
      .apiKeysPost(<ApiKeysPostRequest>{
        login: this.login,
        roles: roles,
      })
      .subscribe((res) => {
        void this.dialogService
          .alert({title: $localize`:@@api-key.dialog.title:Clé d'API`, text: res})
          .then(() => this.refreshApi());
      });
  }

  private refreshApi() {
    this.result$ = this.authenticationService.apiKeysGet();
  }

  public delete(id: number): void {
    this.authenticationService
      .apiKeysIdDelete(id)
      .subscribe(() => this.refreshApi());
  }
}
