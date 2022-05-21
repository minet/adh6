import { Component } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { Router, RoutesRecognized } from '@angular/router';
import { Configuration } from './api';
import { Subject } from 'rxjs';
import { ErrorPageService } from './error-page.service';
import { SessionService } from './session.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  currentPageAuthBypass = false;
  hasError: Subject<boolean> = this.errorPageService.hasError;

  constructor(
    private oauthService: OAuthService,
    private configurationAPI: Configuration,
    private sessionService: SessionService,
    private router: Router,
    private errorPageService: ErrorPageService,
  ) {
    this.sessionService.checkSession();

    router.events.subscribe(event => {
      if (event instanceof RoutesRecognized) {
        this.hasError.next(false);
        const r = event.state.root.firstChild;
        this.currentPageAuthBypass = Boolean(r.data['bypassAuth']);
      }
    });
  }

  isAuthenticated() {
    return (this.currentPageAuthBypass || this.oauthService.hasValidAccessToken()) && this.configurationAPI.accessToken != "";
  }

  getCurrentComponent() {
    let state = this.router.routerState.root;

    while (state.firstChild) {
      state = state.firstChild;
    }

    const stateComponent = <any>state.component;
    return stateComponent ? stateComponent.name : '';
  }
}
