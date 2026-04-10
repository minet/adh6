import {Injectable} from "@angular/core";
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from "@angular/common/http";
import {Observable, from} from "rxjs";
import {OidcSecurityService} from "angular-auth-oidc-client";
import {switchMap} from "rxjs/operators";

@Injectable()
export class AuthTokenInterceptor implements HttpInterceptor {
  constructor(private readonly oidcSecurityService: OidcSecurityService) {}

  intercept(
    req: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    return from(this.oidcSecurityService.getAccessToken()).pipe(
      switchMap((token) => {
        if (token) {
          const cloned = req.clone({
            setHeaders: {
              Authorization: `Bearer ${token}`,
            },
          });
          return next.handle(cloned);
        }
        return next.handle(req);
      }),
    );
  }
}
