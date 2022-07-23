import { Injectable } from '@angular/core';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { NotificationService } from '../notification.service';
import { Router } from '@angular/router';
import { SessionService } from '../session.service';

@Injectable()
export class NotifInterceptor implements HttpInterceptor {
  constructor(
    private notificationService: NotificationService,
    private router: Router,
    private sessionService: SessionService
  ) { }

  intercept(req: HttpRequest<any>, next: HttpHandler):
    Observable<HttpEvent<any>> {
    // Check that the request is for the API server
    // if there is an error, notify
    return next.handle(req).pipe(
      catchError(response => {
        let err = {
          code: 200,
          message: ''
        };
        if (response.error.code === undefined) {
          err = {
            code: response.status,
            message: response.statusText
          };
        } else {
          err = response.error;
        }
        if (err.code === 401) {
          this.sessionService.logout();
          this.router.navigate(['/error', err.code]);
        } else {
          if (req.method === 'GET' && req.headers.get('x-critical-error') === 'true') {
            this.router.navigate(['/error', err.code]);
          }
        }
        this.notificationService.errorNotification(+err.code, err.code + ' on ' + req.url, err.message, 3000);
        return throwError(response);
      }),
    );

  }
}
