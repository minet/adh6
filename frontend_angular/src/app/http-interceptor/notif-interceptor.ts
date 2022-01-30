import {Injectable} from '@angular/core';
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';

import {Observable, throwError} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {ErrorPageService} from '../error-page.service';
import { NotificationService } from '../notification.service';
import { Router } from '@angular/router';

@Injectable()
export class NotifInterceptor implements HttpInterceptor {
  constructor(
    private notificationService: NotificationService,
    private errorPageService: ErrorPageService,
    private router: Router
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
            this.router.navigate(['/dashboard'])
          } else {
            if (req.method === 'GET' && req.headers.get('x-critical-error') === 'true') {
              this.errorPageService.show(err);
            } else {
              this.notificationService.errorNotification(+err.code, err.code + ' on ' + req.url, err.message, 3000);
            }
          }
          return throwError(response);
        }),
      );

  }
}
