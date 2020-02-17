import {Component, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {JwksValidationHandler, OAuthService} from 'angular-oauth2-oidc';
import {authConfig, authBypass} from './config/auth.config';
import {NAINA_FIELD, NAINA_PREFIX} from './config/naina.config';
import {ActivatedRoute, Router, RoutesRecognized} from '@angular/router';
import {filter, first, map, takeWhile} from 'rxjs/operators';
import { faBug } from '@fortawesome/free-solid-svg-icons';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {BugReportService} from './api';
import {NotificationsService} from 'angular2-notifications';
import {BugReport} from './api/model/bugReport';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  titre = 'ADH6';
  faBug = faBug;
  submitBugForm: FormGroup;
  currentPageAuthBypass = false;

  @ViewChild('bugReportModal') bugReportModal;

  constructor(
    private fb: FormBuilder,
    private oauthService: OAuthService,
    private route: ActivatedRoute,
    private router: Router,
    private _service: NotificationsService,
    private bugReportSevice: BugReportService,
  ) {
    this.configureWithNewConfigApi();
    this.createForm();
    router.events.subscribe(event => {
      if (event instanceof RoutesRecognized) {
        const r = event.state.root.firstChild;
        this.currentPageAuthBypass = !!r.data['bypassAuth'];
      }
    });
  }

  createForm() {
    this.submitBugForm = this.fb.group({
      bugTitle: ['', Validators.required],
      bugDescription: ['', Validators.required]
    });
  }

  isAuthenticated() {
    return authBypass || this.oauthService.hasValidAccessToken();
  }

  needsAuth() {
    return !this.currentPageAuthBypass;
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
    const bugReport: BugReport = {
      'title': this.submitBugForm.value.bugTitle,
      'description': this.submitBugForm.value.bugDescription,
    };

    this.bugReportSevice.bugReportPost(bugReport)
      .subscribe((res) => {
        this.bugReportModal.hide();
        this.submitBugForm.reset();
        this._service.success('Ok!', 'Bug envoyé avec succès ');
      });
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

    this.oauthService.loadDiscoveryDocumentAndTryLogin({
      onTokenReceived: (info) => {
        this.oauthService.loadUserProfile();
        // this.router.navigate(['/member/view', this.oauthService.getIdentityClaims().sub]);
      }
    });
  }

}

