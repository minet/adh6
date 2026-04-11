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
import {catchError, switchMap} from "rxjs/operators";

@Injectable()
export class AuthTokenInterceptor implements HttpInterceptor {
  constructor(private readonly oidcSecurityService: OidcSecurityService) {}

  intercept(
    req: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    // Never attach a Bearer token to auth endpoints — they are unauthenticated
    // by design and the backend middleware would reject an expired token.
    if (req.url.includes("/api/auth/")) {
      return next.handle(req);
    }

    return this.oidcSecurityService.getAccessToken().pipe(
      switchMap((token) => {
        const authReq = token
          ? req.clone({setHeaders: {Authorization: `Bearer ${token}`}})
          : req;
        return next.handle(authReq).pipe(
          catchError((error: HttpErrorResponse) => {
            if (error.status === 401) {
              return this.oidcSecurityService.forceRefreshSession().pipe(
                switchMap(() => this.oidcSecurityService.getAccessToken()),
                switchMap((newToken) => {
                  const retryReq = newToken
                    ? req.clone({
                        setHeaders: {Authorization: `Bearer ${newToken}`},
                      })
                    : req;
                  return next.handle(retryReq);
                }),
                catchError(() => throwError(() => error)),
              );
            }
            return throwError(() => error);
          }),
        );
      }),
    );
  }
}
