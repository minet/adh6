import {
  HttpErrorResponse,
  HttpHandlerFn,
  HttpInterceptorFn,
  HttpRequest,
} from "@angular/common/http";
import {inject} from "@angular/core";
import {catchError, switchMap, throwError} from "rxjs";
import {environment} from "../../environments/environment";
import {AuthService} from "./auth.service";

function isUnauthorized(error: unknown): boolean {
  return error instanceof HttpErrorResponse && error.status === 401;
}

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
) => {
  if (!req.url.startsWith(environment.API_BASE_PATH)) return next(req);

  const request = req.clone({
    setHeaders: {"X-Requested-With": "XMLHttpRequest"},
  });
  if (req.url.startsWith(`${environment.API_BASE_PATH}/auth/`)) {
    return next(request);
  }

  const auth = inject(AuthService);
  return next(request).pipe(
    catchError((error: unknown) => {
      if (!isUnauthorized(error)) return throwError(() => error);
      return auth.refreshSession().pipe(
        catchError((refreshError: unknown) => {
          if (isUnauthorized(refreshError)) auth.expireSession();
          return throwError(() => error);
        }),
        switchMap(() =>
          next(request).pipe(
            catchError((retryError: unknown) => {
              if (isUnauthorized(retryError)) auth.expireSession();
              return throwError(() => retryError);
            }),
          ),
        ),
      );
    }),
  );
};
