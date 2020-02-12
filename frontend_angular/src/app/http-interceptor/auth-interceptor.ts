import {Injectable} from '@angular/core';
import {OAuthService} from 'angular-oauth2-oidc';

import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';

import {Observable} from 'rxjs';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(public oauthService: OAuthService) {
  }

  intercept(req: HttpRequest<any>, next: HttpHandler):
    Observable<HttpEvent<any>> {
    // Check that the request is for the API server
    // if so, add the authentication header
    req = req.clone({
      setHeaders: {
        Authorization: this.oauthService.authorizationHeader()
      }
    });
    return next.handle(req);
  }
}
