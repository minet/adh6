import {Component, OnDestroy, OnInit, ViewChild} from '@angular/core';
import { OAuthService} from 'angular-oauth2-oidc';
import {authBypass, authConfig} from './config/auth.config';
import {NAINA_FIELD, NAINA_PREFIX} from './config/naina.config';
import {ActivatedRoute, Router, RoutesRecognized} from '@angular/router';
import {filter, first, map} from 'rxjs/operators';
import {faBug} from '@fortawesome/free-solid-svg-icons';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {BugReport, Member, MiscService} from './api';
import {NotificationsService} from 'angular2-notifications';
import {Subject} from 'rxjs';
import {ErrorPageService} from './error-page.service';
import {Ability, AbilityBuilder} from '@casl/ability';
import {JsonFormatter} from 'tslint/lib/formatters';

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

  hasError: Subject<boolean> = this.errorPageService.hasError;

  @ViewChild('bugReportModal') bugReportModal;

  constructor(
    private fb: FormBuilder,
    private oauthService: OAuthService,
    private route: ActivatedRoute,
    private router: Router,
    private _service: NotificationsService,
    private miscService: MiscService,
    private errorPageService: ErrorPageService,
    private ability: Ability
  ) {
    this.configureWithNewConfigApi();
    this.createForm();

    router.events.subscribe(event => {
      if (event instanceof RoutesRecognized) {
        this.hasError.next(false);
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
      title: this.submitBugForm.value.bugTitle,
      description: this.submitBugForm.value.bugDescription,
      labels: [],
    };

    this.miscService.bugReportPost(bugReport)
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

  loadProfileAndSetupAbilities() {
    if (this.oauthService.hasValidAccessToken()) {
      this.miscService.profile().subscribe(
        (profile) => {
          const roles = profile.admin.roles;
          localStorage.setItem('roles', roles.join(','));
          localStorage.setItem('admin_member', JSON.stringify(profile.admin.member as Member));

          const { can, rules } = new AbilityBuilder();

          if (roles.indexOf('adh6_admin') !== -1) {
            can('manage', 'all');
          } else {
            can('manage', 'Member', { id: (profile.admin.member as Member).id });
            can('read', 'all');
          }

          // @ts-ignore
          this.ability.update(rules);
        });
    }
  }

  private configureWithNewConfigApi() {
    this.oauthService.events
      .pipe(filter(e => e.type === 'token_received'))
      .subscribe(_ => {
        this.oauthService.loadUserProfile();
        this.loadProfileAndSetupAbilities();
      });
    this.oauthService.loadDiscoveryDocumentAndTryLogin();
    this.loadProfileAndSetupAbilities();
  }

}

