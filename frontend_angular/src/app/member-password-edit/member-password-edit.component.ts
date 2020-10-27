import {Component, OnInit} from '@angular/core';
import {AbstractControl, FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {NotificationsService} from 'angular2-notifications';
import {finalize, first, map, switchMap, tap} from 'rxjs/operators';
import {Observable} from 'rxjs';
import {MemberService} from '../api';
import { md4 } from 'hash-wasm';
import {Location} from '@angular/common';

function passwordConfirming(c: AbstractControl): any {
  if (!c || !c.value) {
    return;
  }
  const pwd = c.value['password'];
  const cpwd = c.value['password_confirm'];

  if (!pwd || !cpwd) {
    return;
  }
  if (pwd !== cpwd) {
    return {invalid: true};
  }
}

@Component({
  selector: 'app-member-password-edit',
  templateUrl: './member-password-edit.component.html',
  styleUrls: ['./member-password-edit.component.css']
})
export class MemberPasswordEditComponent implements OnInit {

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private notif: NotificationsService,
    private route: ActivatedRoute,
    private memberService: MemberService,
    private location: Location
  ) {
  }

  disabled = false;
  memberPassword: FormGroup;

  /*
  Taken from https://stackoverflow.com/a/37597001
   */
  strEncodeUTF16(str) {
    const buf = new ArrayBuffer(str.length * 2);
    const bufView = new Uint16Array(buf);
    for (let i = 0, strLen = str.length; i < strLen; i++) {
      bufView[i] = str.charCodeAt(i);
    }
    return bufView;
  }

  ngOnInit() {
    this.createForm();
  }

  createForm(): void {
    this.memberPassword = this.fb.group({
      password: ['', [Validators.required, Validators.minLength(8)]],
      password_confirm: ['', [Validators.required, Validators.minLength(8)]],
    }, {
      validator: passwordConfirming
    });
  }


  changePassword(): void {
    md4(this.strEncodeUTF16(this.memberPassword.value.password)).then((hashedPassword) => {
    this.getMemberId()
      .pipe(
        first(),
        switchMap(member_id => this.updatePasswordOfUser(member_id, hashedPassword)),
        finalize(() => this.disabled = false)
      )
      .subscribe((_) => {
      });
    });
  }

  private updatePasswordOfUser(member_id: string, hashedPasswordVar: string) {
    return this.memberService.memberMemberIdPasswordPut(
      {hashedPassword: hashedPasswordVar},
      +member_id,
      'response')
      .pipe(
        first(),
        tap((response) => {
          this.location.back();
          this.notif.success(response.status + ': Success');
        }),
      );

  }

  private getMemberId(): Observable<string> {
    return this.route.paramMap.pipe(
      map(params => params.get('member_id')),
      first(),
    );
  }
}
