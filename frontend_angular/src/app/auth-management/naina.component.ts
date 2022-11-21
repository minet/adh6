import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';
import { AuthenticationService, RoleMapping, Role, RoleGetRequest } from '../api';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  selector: 'app-naina',
  template: `
  <div class="level">
    <div class="level-item is-fullwidth mr-2">
      <input class="input" placeholder="Identifiant" type="text" [(ngModel)]="login" />
    </div>
    <div class="level-right">
      <div class="level-item">
        <button class="button is-primary" (click)="newNainA()">Nouveau NainA</button>
      </div>
    </div>
  </div>
  <ng-container *ngIf="result$ | async as result; else loadingTable">
    <table class="table is-fullwidth">
      <thead>
        <tr>
          <th>Login</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
        <tr *ngFor="let mapping of result">
          <td>{{ mapping.identifier }}</td>
          <td>{{ mapping.role }}</td>
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
export class NainaComponent implements OnInit {
  public result$: Observable<RoleMapping[]>;
  public login = "";

  constructor(
    private authenticationService: AuthenticationService
  ) { }

  ngOnInit(): void {
    this.refreshNainA();
  }

  public newNainA(): void {
    this.authenticationService.rolePost(<RoleGetRequest>{
      identifier: this.login,
      roles: [
        Role.Adminread,
        Role.Adminwrite,
        Role.Networkread,
        Role.Networkwrite
      ],
      auth: 'user',
    }).subscribe(() => this.refreshNainA());
  }

  private refreshNainA() {
    this.result$ = this.authenticationService.roleGet('user');
  }
}
