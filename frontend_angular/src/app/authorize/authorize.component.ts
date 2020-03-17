import {Component, OnInit, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {BehaviorSubject, Subject} from 'rxjs';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {SCOPE_LIST} from '../config/scope.config';
import * as urlParse from 'url-parse';

class AuthorizationResponse {
  username: string;
  scope: string;
  client_name: string;
  return_uri: string;
}

@Component({
  selector: 'app-authorize',
  templateUrl: './authorize.component.html',
  encapsulation: ViewEncapsulation.None,
  styleUrls: ['./authorize.component.css']
})
export class AuthorizeComponent implements OnInit {

  constructor(private route: ActivatedRoute, private fb: FormBuilder, ) {
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
      const obj = JSON.parse(atob(fragment));
      this.return_uri = obj.return_uri;
      this.authorization$.next(obj);

      const objScope = obj.scope.split(' ');
      const scope = new Array<string>();
      for (let i = 0; i < objScope.length; i++) {
        scope.push(objScope[i]);
        this.consents.set(objScope[i], true);
      }

      this.scope$.next(scope);
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
    form.appendChild(AuthorizeComponent.createHiddenElement('confirm', '1'));
    window.document.body.appendChild(form);
    form.submit();
  }

}
