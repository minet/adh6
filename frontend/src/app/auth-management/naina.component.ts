import {CommonModule} from "@angular/common";
import {Component, OnInit} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {Observable} from "rxjs";
import {
  AuthenticationService,
  RoleMapping,
  Role,
  RolePostRequest,
} from "../api";

@Component({
  imports: [CommonModule, FormsModule],
  selector: "app-naina",
  template: `
    <div class="level">
      <div class="level-item is-fullwidth mr-2">
        <input
          class="input"
          placeholder="Identifiant"
          type="text"
          [(ngModel)]="login" />
      </div>
      <div class="level-right">
        <div class="level-item">
          <button class="button is-primary" (click)="newNainA()">
            Nouveau NainA
          </button>
        </div>
      </div>
    </div>
    @if (result$ | async; as result) {
      <table class="table is-fullwidth">
        <thead>
          <tr>
            <th>Login</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          @for (mapping of result; track mapping) {
            <tr>
              <td>{{ mapping.identifier }}</td>
              <td>{{ mapping.role }}</td>
            </tr>
          }
        </tbody>
      </table>
    } @else {
      <div class="notification is-info is-light has-text-centered">
        <h4 class="title is-4">Chargement ...</h4>
      </div>
    }
  `,
})
export class NainaComponent implements OnInit {
  public result$: Observable<RoleMapping[]> = new Observable<RoleMapping[]>();
  public login = "";

  constructor(private readonly authenticationService: AuthenticationService) {}

  ngOnInit(): void {
    this.refreshNainA();
  }

  public newNainA(): void {
    this.authenticationService
      .rolePost(<RolePostRequest>{
        identifier: this.login,
        roles: [
          Role.AdminRead,
          Role.AdminWrite,
          Role.NetworkRead,
          Role.NetworkWrite,
        ],
        auth: "user",
      })
      .subscribe(() => this.refreshNainA());
  }

  private refreshNainA() {
    this.result$ = this.authenticationService.roleGet("user");
  }
}
