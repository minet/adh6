import {Injectable} from "@angular/core";
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpErrorResponse,
} from "@angular/common/http";

import {Observable, throwError} from "rxjs";
import {catchError} from "rxjs/operators";
import {NotificationService} from "../notification.service";

interface ApiError {
  code: number;
  message: string;
}

@Injectable()
export class NotifInterceptor implements HttpInterceptor {
  constructor(private notificationService: NotificationService) {}

  intercept(
    req: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    // Check that the request is for the API server
    // if there is an error, notify
    return next.handle(req).pipe(
      catchError((response: HttpErrorResponse) => {
        let err: ApiError = {
          code: 200,
          message: "",
        };
        const errorBody = response.error as Partial<ApiError>;
        if (errorBody?.code === undefined) {
          err = {
            code: response.status,
            message: response.statusText,
          };
        } else {
          err = errorBody as ApiError;
        }
        if (err.code === 401) {
          if (window.location.href !== "/portail") {
            window.location.href = "/portail";
          }
        }
        if (err.code !== 404) {
          this.notificationService.errorNotification(
            +err.code,
            err.code + " on " + req.url,
            err.message,
            3000,
          );
        }
        return throwError(response);
      }),
    );
  }
}
