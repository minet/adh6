import {Injectable} from '@angular/core';
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';

import {Observable, throwError} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {authConfig} from '../config/auth.config';
import {ErrorPageService} from '../error-page.service';
import {OAuthService} from 'angular-oauth2-oidc';
import { AppConstantsService } from '../app-constants.service';

@Injectable()
export class NotifInterceptor implements HttpInterceptor {
  constructor(
    private appConstant: AppConstantsService,
    private errorPageService: ErrorPageService,
    private oauthService: OAuthService) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler):
    Observable<HttpEvent<any>> {
    const api_url = authConfig.redirectUri;
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
            this.oauthService.logOut();
          } else {
            if (req.method === 'GET' && req.headers.get('x-critical-error') === 'true') {
              this.errorPageService.show(err);
            } else {
              this.appConstant.Toast.fire({
                title: err.code + ' on ' + req.url,
                text: err.message,
                icon: 'error',
                timer: 3000
              });
            }
          }
          return throwError(response);
        }),
      );

  }
}
