import {Component, OnDestroy, OnInit} from '@angular/core';
import {JwksValidationHandler, OAuthService} from 'angular-oauth2-oidc';
import {authConfig, authBypass} from './config/auth.config';
import {NAINA_FIELD, NAINA_PREFIX} from './config/naina.config';
import {ActivatedRoute, ActivatedRouteSnapshot, Router} from '@angular/router';
import {filter, first, map} from 'rxjs/operators';
import { faBug } from '@fortawesome/free-solid-svg-icons';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  titre = 'ADH6';
  faBug = faBug;
  submitBugForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private oauthService: OAuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.configureWithNewConfigApi();
    this.createForm();
  }

  createForm() {
    this.submitBugForm = this.fb.group({
      bugTitle: ['', Validators.required]
    });
  }

  isAuthenticated() {
    return authBypass || this.oauthService.hasValidAccessToken();
  }

  ngOnInit() {
    this.isAuthenticated();
    this.route.fragment
      .pipe(
        filter((fragment) => fragment != null && fragment.startsWith(NAINA_FIELD + NAINA_PREFIX)),
        map((fragment) => fragment.substring(NAINA_FIELD.length)),
        first(),
      )
      .subscribe((token) => {
        if (this.isAuthenticated()) {
          alert('Vous êtes déjà authentifié.');
          return;
        }
        sessionStorage.setItem('access_token', token);
        sessionStorage.setItem('granted_scopes', '["profile"]');
        sessionStorage.setItem('access_token_stored_at', '' + Date.now());

        // const pathWithoutHash = this.location.path(false);
        // this.location.replaceState(pathWithoutHash);
      });
  }

  ngOnDestroy() {
  }

  onSubmitBug() {

  }

  getCurrentComponent() {
    let state = this.router.routerState.root;

    while (state.firstChild) {
      state = state.firstChild;
    }

    const stateComponent = <any>state.component;
    return stateComponent ? stateComponent.name : '';
  }

  private configureWithNewConfigApi() {
    this.oauthService.configure(authConfig);
    this.oauthService.tokenValidationHandler = new JwksValidationHandler();
    this.oauthService.tryLogin();
  }

}

