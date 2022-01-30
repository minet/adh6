import {Component, ViewChild} from '@angular/core';
import {OAuthService} from 'angular-oauth2-oidc';
import {authBypass} from './config/auth.config';
import {Router, RoutesRecognized} from '@angular/router';
import {faBug} from '@fortawesome/free-solid-svg-icons';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {BugReport, MiscService, Configuration} from './api';
import {Subject} from 'rxjs';
import {ErrorPageService} from './error-page.service';
import { NotificationService } from './notification.service';
import {SessionService} from './session.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  faBug = faBug;
  submitBugForm: FormGroup;
  currentPageAuthBypass = false;

  hasError: Subject<boolean> = this.errorPageService.hasError;

  @ViewChild('bugReportModal') bugReportModal;

  constructor(
    private fb: FormBuilder,
    private oauthService: OAuthService,
    private configurationAPI: Configuration,
    private sessionService: SessionService,
    private router: Router,
    private notificationService: NotificationService,
    private miscService: MiscService,
    private errorPageService: ErrorPageService,
  ) {
    this.sessionService.checkSession();
    this.createForm();

    router.events.subscribe(event => {
      if (event instanceof RoutesRecognized) {
        this.hasError.next(false);
        const r = event.state.root.firstChild;
        this.currentPageAuthBypass = Boolean(r.data['bypassAuth']);
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
    return (this.currentPageAuthBypass || authBypass || this.oauthService.hasValidAccessToken()) && this.configurationAPI.accessToken != "";
  }

  onSubmitBug() {
    const bugReport: BugReport = {
      title: this.submitBugForm.value.bugTitle,
      description: this.submitBugForm.value.bugDescription,
      labels: [],
    };

    this.miscService.bugReportPost(bugReport)
      .subscribe(_ => {
        this.bugReportModal.hide();
        this.submitBugForm.reset();
        this.notificationService.successNotification('Ok!', 'Bug envoyé avec succès ');
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
}
