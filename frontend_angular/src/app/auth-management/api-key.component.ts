import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';
import Swal from 'sweetalert2';
import { ApiKey, ApiKeysGetRequest, AuthenticationService, Role } from '../api';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  selector: 'app-api-key',
  template: `
  <div class="level">
    <div class="level-item is-fullwidth mr-2">
      <input class="input" placeholder="Identifiant" type="text" [(ngModel)]="login" />
    </div>
    <div class="level-right">
      <div class="level-item">
        <div class="select is-multiple">
          <select [(ngModel)]="roles" multiple size="3">
            <option value="0">Admin</option>
            <option value="1">Network</option>
            <option value="2">Trésorerie</option>
          </select>
        </div>
      </div>
      <div class="level-item">
        <button class="button is-primary" (click)="submit()">Nouvelle clef</button>
      </div>
    </div>
  </div>
  <ng-container *ngIf="result$ | async as result; else loadingTable">
    <table class="table is-fullwidth">
      <thead>
        <tr>
          <th>Login</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr *ngFor="let key of result">
          <td>{{ key.login }}</td>
          <td><button class="button is-danger" (click)="delete(key.id)">Supprimer</button>
        </tr>
      </tbody>
    </table>
  </ng-container>
  <ng-template #loadingTable>
    <div class="notification is-info is-light has-text-centered">
      <h4 class="title is-4">Chargement ...</h4>
    </div>
  </ng-template>
`
})
export class ApiKeyComponent implements OnInit {
  public roleKeys = Object.values(Role);
  public result$: Observable<ApiKey[]>;
  public login: string = "";
  public roles: string[] = [];

  constructor(
    private authenticationService: AuthenticationService
  ) { }

  ngOnInit(): void {
    this.refreshApi();
  }

  public submit(): void {
    if (this.roles.length === 0 || this.login === "") return;

    let roles = [];
    for (let i in this.roles) {
      if (i === "0") {
        roles.push(Role.Adminwrite, Role.Adminread)
      } else if (i === "1") {
        roles.push(Role.Networkwrite, Role.Networkread)
      } else if (i === "2") {
        roles.push(Role.Treasurerwrite, Role.Treasurerread)
      }
    }

    this.authenticationService.apiKeysPost(<ApiKeysGetRequest>{
      login: this.login,
      roles: roles
    }).subscribe((res) => Swal.fire({ 'title': 'Clé d\'API', text: res }).then(() => this.refreshApi()));
  }

  private refreshApi() {
    this.result$ = this.authenticationService.apiKeysGet();
  }

  public delete(id: number): void {
    this.authenticationService.apiKeysIdDelete(id).subscribe(() => this.refreshApi())
  }
}
