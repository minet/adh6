import {Component, OnInit, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {BehaviorSubject, Subject} from 'rxjs';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {SCOPE_LIST} from '../config/scope.config';
import * as urlParse from 'url-parse';
import {OAuthService} from 'angular-oauth2-oidc';
import {falseIfMissing} from 'protractor/built/util';


class AuthorizationResponse {
  username: string;
  scope: string;
  client_name: string;
  return_uri: string;

}

@Component({
  selector: 'app-inscription',
  templateUrl: './inscription.component.html',
  encapsulation: ViewEncapsulation.None,
  styleUrls: ['./inscription.component.css']
})
export class InscriptionComponent implements OnInit {

  constructor(private oauthService: OAuthService, private route: ActivatedRoute, private fb: FormBuilder, ) {
  }

  public authorization$: BehaviorSubject<AuthorizationResponse> = new BehaviorSubject<AuthorizationResponse>(null);
  public scope$: BehaviorSubject<Array<string>> = new BehaviorSubject<Array<string>>(null);
  public consents = new Map<string, any>();
  public return_uri = '';

  SCOPE_LIST = SCOPE_LIST;

  private static createHiddenElement(name: string, value: string): HTMLInputElement {
    const hiddenField = document.createElement('input');
    hiddenField.setAttribute('name', name);
    hiddenField.setAttribute('value', value);
    hiddenField.setAttribute('type', 'hidden');
    return hiddenField;
  }

  ngOnInit() {
    this.route.fragment.subscribe((fragment: string) => {
    });
  }

  onSubmit($event) {
    const form = window.document.createElement('form');
    form.setAttribute('method', 'POST');
    form.setAttribute('action', this.return_uri);
    form.setAttribute('target', '_self');

    const scope = [];
    this.consents.forEach((value: boolean, key: string) => {
      if (value) {
        scope.push(key);
      }

    });

    const return_uri = urlParse(this.return_uri, true);
    return_uri.query.scope = scope.join(' ');
    form.appendChild(InscriptionComponent.createHiddenElement('confirm', '1'));
    window.document.body.appendChild(form);
    form.submit();
  }

  public login() {
    this.oauthService.initImplicitFlow();
  }

  public setDate(nb: number) {
    const today = new Date();
    today.setMonth(today.getMonth() + nb);
    return today;
  }
}
