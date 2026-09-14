import {Injectable} from "@angular/core";
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpErrorResponse,
} from "@angular/common/http";
import {Observable, throwError} from "rxjs";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {catchError, finalize, shareReplay, switchMap} from "rxjs/operators";
import {environment} from "../../environments/environment";

@Injectable()
export class AuthTokenInterceptor implements HttpInterceptor {
  // Requests failing with 401 at the same time share a single session refresh.
  private refreshedToken$: Observable<string> | null = null;

  constructor(private readonly oidcSecurityService: OidcSecurityService) {}

  intercept(
    req: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    // Keycloak requests from the OIDC library and /api/auth/ must not carry the token.
    if (
      !req.url.startsWith(environment.API_BASE_PATH) ||
      req.url.includes("/api/auth/")
    ) {
      return next.handle(req);
    }

    return this.oidcSecurityService.getAccessToken().pipe(
      switchMap((token) =>
        next.handle(this.withToken(req, token)).pipe(
          catchError((error: HttpErrorResponse) => {
            if (error.status !== 401) {
              return throwError(() => error);
            }
            return this.refreshToken().pipe(
              switchMap((newToken) =>
                next.handle(this.withToken(req, newToken)),
              ),
              catchError(() => throwError(() => error)),
            );
          }),
        ),
      ),
    );
  }

  private refreshToken(): Observable<string> {
    if (!this.refreshedToken$) {
      this.refreshedToken$ = this.oidcSecurityService
        .forceRefreshSession()
        .pipe(
          switchMap(() => this.oidcSecurityService.getAccessToken()),
          finalize(() => (this.refreshedToken$ = null)),
          shareReplay(1),
        );
    }
    return this.refreshedToken$;
  }

  private withToken(
    req: HttpRequest<unknown>,
    token: string,
  ): HttpRequest<unknown> {
    return token
      ? req.clone({setHeaders: {Authorization: `Bearer ${token}`}})
      : req;
  }
}
