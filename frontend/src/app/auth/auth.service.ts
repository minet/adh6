import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {DOCUMENT} from "@angular/common";
import {Injectable, inject, signal} from "@angular/core";
import {Observable, finalize, firstValueFrom, shareReplay} from "rxjs";
import {environment} from "../../environments/environment";
import {MiscService} from "../api";
import {DialogService} from "../ui/dialog.service";
import {AppAbility, abilityRulesFor} from "./ability";

type Failure = "login-failed" | "unavailable" | "unreachable";

@Injectable({providedIn: "root"})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly document = inject(DOCUMENT);
  private readonly ability = inject(AppAbility);
  private readonly misc = inject(MiscService);
  private readonly dialogs = inject(DialogService);

  private readonly _isAuthenticated = signal(false);
  private pendingRefresh$: Observable<void> | null = null;
  // Once true, nothing signs the user in again by itself: they choose to retry.
  private stopped = false;
  private redirecting = false;

  readonly isAuthenticated = this._isAuthenticated.asReadonly();

  /** Reports a failed login, otherwise finds out who is signed in and what they may do. */
  async initialize(): Promise<void> {
    const failure = this.takeLoginFailure();
    if (failure) {
      this.fail(failure);
      return;
    }
    try {
      const profile = await firstValueFrom(this.misc.profile());
      this.ability.update(abilityRulesFor(profile));
      this._isAuthenticated.set(true);
    } catch (error) {
      this.ability.update([]);
      // Only a 401 means nobody is signed in, and the interceptors are already sending the user
      // to Keycloak. Anything else is an outage, which signing in again would not fix.
      if (!(error instanceof HttpErrorResponse && error.status === 401)) {
        this.fail("unreachable");
      }
    }
  }

  /** Signs the user in unless an earlier attempt just failed; `routerUrl` is where to come back to. */
  requireLogin(routerUrl: string): void {
    this.requireLoginAt(this.sitePath(routerUrl));
  }

  logout(): void {
    this.forget();
    this.http
      .post<{
        logout_url: string;
      }>(`${environment.API_BASE_PATH}/auth/logout`, null)
      .subscribe({
        next: ({logout_url}) => this.navigate(logout_url),
        error: () => this.navigate(this.document.baseURI),
      });
  }

  /** The session can no longer be renewed: sign in again, on the current page. */
  expireSession(): void {
    if (this.stopped || this.redirecting) return;
    this.forget();
    this.requireLoginAt(this.currentPath());
  }

  /** Concurrent callers share a single renewal, refresh tokens being single use. */
  refreshSession(): Observable<void> {
    this.pendingRefresh$ ??= this.http
      .post<void>(`${environment.API_BASE_PATH}/auth/refresh`, null)
      .pipe(
        finalize(() => (this.pendingRefresh$ = null)),
        shareReplay(1),
      );
    return this.pendingRefresh$;
  }

  private requireLoginAt(path: string): void {
    if (this.stopped || this.redirecting) return;
    this.startLogin(path);
  }

  private startLogin(path: string): void {
    this.stopped = false;
    this.redirecting = true;
    this.navigate(
      `${environment.API_BASE_PATH}/auth/login?return_to=${encodeURIComponent(path)}`,
    );
  }

  private forget(): void {
    this._isAuthenticated.set(false);
    this.ability.update([]);
  }

  private fail(failure: Failure): void {
    this.stopped = true;
    this.forget();
    const text = {
      "login-failed": $localize`:@@auth.failure.login-failed:La connexion a échoué. Veuillez réessayer.`,
      unavailable: $localize`:@@auth.failure.unavailable:Le service de connexion est momentanément indisponible. Réessayez dans quelques instants.`,
      unreachable: $localize`:@@auth.failure.unreachable:Le serveur est momentanément indisponible. Réessayez dans quelques instants.`,
    }[failure];
    void this.dialogs
      .confirm({
        title: $localize`:@@auth.failure.title:Connexion impossible`,
        text,
        confirmText: $localize`:@@auth.failure.retry:Réessayer`,
      })
      .then((retry) => {
        if (!retry) return;
        // Nothing wrong with the session itself: just look again.
        if (failure === "unreachable") this.document.location.reload();
        else this.startLogin(this.currentPath());
      });
  }

  private takeLoginFailure(): Failure | null {
    const url = new URL(this.document.location.href);
    const reason = url.searchParams.get("auth_error");
    if (reason === null) return null;
    url.searchParams.delete("auth_error");
    this.document.defaultView?.history.replaceState(null, "", url);
    return reason === "provider_unavailable" ? "unavailable" : "login-failed";
  }

  private sitePath(routerUrl: string): string {
    const url = new URL(routerUrl.replace(/^\//, ""), this.document.baseURI);
    return url.pathname + url.search;
  }

  private currentPath(): string {
    const {pathname, search} = this.document.location;
    return pathname + search;
  }

  private navigate(url: string): void {
    this.document.location.assign(url);
  }
}
