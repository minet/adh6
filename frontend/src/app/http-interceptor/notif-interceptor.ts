import {HttpErrorResponse, HttpInterceptorFn} from "@angular/common/http";
import {inject} from "@angular/core";
import {catchError, throwError} from "rxjs";
import {NotificationService} from "../notification.service";
import {detailOf} from "../shared/http-error";

interface ApiError {
  code: number;
  message: string;
}

/** Reports API failures as toasts. */
export const notifInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);

  return next(req).pipe(
    catchError((response: HttpErrorResponse) => {
      // The authentication interceptor turns a lost session into a message on the portal.
      if (response.status === 401) {
        return throwError(() => response);
      }
      const body = response.error as Partial<ApiError> | null;
      const err: ApiError =
        body?.code === undefined
          ? {
              code: response.status,
              message: detailOf(response, response.statusText),
            }
          : (body as ApiError);

      if (err.code !== 404) {
        notifications.errorNotification(
          +err.code,
          err.code + " on " + req.url,
          err.message,
          3000,
        );
      }
      return throwError(() => response);
    }),
  );
};
