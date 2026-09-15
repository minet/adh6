import {CommonModule} from "@angular/common";
import {Component, OnInit} from "@angular/core";
import {FormsModule} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Observable} from "rxjs";
import {Naina, NainaService} from "../api";
import {NotificationService} from "../notification.service";

@Component({
  imports: [CommonModule, FormsModule],
  selector: "app-naina",
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
          <button
            class="button is-primary"
            [disabled]="login.trim() === ''"
            (click)="newNainA()"
            i18n="@@naina.new">
            Nouveau NainA
          </button>
        </div>
      </div>
    </div>
    @if (nainas$ | async; as nainas) {
      <table class="table is-fullwidth">
        <thead>
          <tr>
            <th>Login</th>
            <th i18n="@@naina.expires">Expire le</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          @for (naina of nainas; track naina.login) {
            <tr>
              <td>{{ naina.login }}</td>
              <td>{{ naina.expires_at | date: "dd/MM/yyyy HH:mm" }}</td>
              <td class="has-text-right">
                <button
                  class="button is-danger is-small"
                  (click)="revokeNainA(naina.login)"
                  i18n="@@naina.revoke">
                  Révoquer
                </button>
              </td>
            </tr>
          } @empty {
            <tr>
              <td colspan="3" class="has-text-centered" i18n="@@naina.none">Aucun NainA actif</td>
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
export class NainaComponent implements OnInit {
  public nainas$: Observable<Naina[]> = new Observable<Naina[]>();
  public login = "";

  constructor(
    private readonly nainaService: NainaService,
    private readonly notificationService: NotificationService,
  ) {}

  ngOnInit(): void {
    this.refreshNainA();
  }

  public newNainA(): void {
    const login = this.login.trim();
    if (login === "") {
      return;
    }
    this.nainaService.nainaPost(login).subscribe({
      next: () => {
        this.notificationService.successNotification(
          $localize`:@@naina.created:NainA créé`,
          login,
        );
        this.login = "";
        this.refreshNainA();
      },
      error: (err: HttpErrorResponse) => {
        if (err.status === 404) {
          this.notificationService.errorNotification(
            404,
            $localize`:@@naina.user-not-found:Utilisateur introuvable`,
            $localize`:@@naina.user-not-found.desc:Aucun adhérent avec le login « ${login}:login: »`,
          );
        }
      },
    });
  }

  public revokeNainA(login: string): void {
    this.nainaService.nainaDelete(login).subscribe(() => this.refreshNainA());
  }

  private refreshNainA() {
    this.nainas$ = this.nainaService.nainaGet();
  }
}
