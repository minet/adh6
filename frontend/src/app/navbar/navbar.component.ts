import {Component, LOCALE_ID, inject} from "@angular/core";
import {AsyncPipe, CommonModule} from "@angular/common";
import {RouterModule} from "@angular/router";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {AblePipe} from "@casl/angular";
import {ThemeService} from "../theme.service";

@Component({
  standalone: true,
  imports: [AsyncPipe, CommonModule, RouterModule, AblePipe],
  selector: "app-navbar",
  templateUrl: "./navbar.component.html",
  styles: `
    .nav-brand {
      padding-inline: 1.25rem;
    }
    .nav-brand:hover,
    .nav-brand:focus {
      background-color: transparent;
    }
    .nav-brand img {
      height: 1.9rem;
      max-height: 1.9rem;
      width: auto;
    }
    .nav-actions {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding-inline: 1.25rem;
    }

    .nav-lang,
    .nav-btn {
      height: 2.125rem;
      border: 1px solid hsl(214 22% 20%);
      border-radius: 0.5rem;
      background: hsl(214 30% 10%);
    }

    .nav-lang {
      display: inline-flex;
      padding: 2px;
      gap: 2px;
    }
    .nav-lang a {
      display: grid;
      place-items: center;
      min-width: 2.25rem;
      border-radius: 0.375rem;
      color: hsl(214 16% 60%);
      font-size: 0.75rem;
      font-weight: 600;
      transition: color 150ms;
    }
    .nav-lang a:hover {
      color: hsl(214 30% 92%);
    }
    .nav-lang a.is-current {
      background: hsl(214 26% 20%);
      color: hsl(214 30% 96%);
    }

    .nav-btn {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding-inline: 0.75rem;
      color: hsl(214 22% 80%);
      font: inherit;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition:
        border-color 150ms,
        color 150ms,
        background-color 150ms;
    }
    .nav-btn:hover {
      border-color: hsl(214 22% 32%);
      color: hsl(214 30% 96%);
    }
    .nav-btn.is-icon {
      justify-content: center;
      width: 2.125rem;
      padding: 0;
    }
    .nav-btn.is-icon:hover {
      color: #71cff1;
    }
    .nav-btn.is-icon i {
      animation: theme-spin 300ms ease-out;
    }
    .nav-logout:hover {
      border-color: hsl(4 60% 45%);
      background: hsl(4 60% 45% / 0.15);
      color: hsl(4 90% 78%);
    }

    @keyframes theme-spin {
      from {
        opacity: 0;
        transform: rotate(-90deg) scale(0.6);
      }
    }
  `,
})
export class NavbarComponent {
  protected readonly theme = inject(ThemeService);
  protected readonly isEnglish = inject(LOCALE_ID).startsWith("en");
  public isMenuActive = false;
  constructor(public oidcSecurityService: OidcSecurityService) {}

  logout() {
    this.oidcSecurityService
      .logoff()
      .subscribe((result) => console.log(result));
  }
}
