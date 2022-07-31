import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { finalize, first, map, switchMap, tap } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { MemberService } from '../api';
import { md4 } from 'hash-wasm';
import { Location } from '@angular/common';
import { NotificationService } from '../notification.service';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';

function passwordConfirming(c: AbstractControl): ValidationErrors | null {
  if (!c || !c.value) {
    return;
  }
  const pwd = c.value['password'];
  const cpwd = c.value['password_confirm'];

  if (!pwd || !cpwd) {
    return;
  }
  if (pwd !== cpwd) {
    return { invalid: true };
  }
}

@Component({
  selector: 'app-member-password-edit',
  templateUrl: './member-password-edit.component.html',
  styleUrls: ['./member-password-edit.component.css']
})
export class MemberPasswordEditComponent implements OnInit {
  public showPassword: boolean = false;
  public showConfirmPassword: boolean = false;

  faEye = faEye;
  faEyeSlash = faEyeSlash;

  constructor(
    private fb: FormBuilder,
    private notificationService: NotificationService,
    private route: ActivatedRoute,
    private memberService: MemberService,
    private location: Location
  ) { }

  disabled = false;
  memberPassword: FormGroup;

  /*
  Taken from https://stackoverflow.com/a/37597001
   */
  strEncodeUTF16(str: string) {
    const buf = new ArrayBuffer(str.length * 2);
    const bufView = new Uint16Array(buf);
    for (let i = 0, strLen = str.length; i < strLen; i++) {
      bufView.set([str.charCodeAt(i)], i);
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
    return this.memberService.memberIdPasswordPut(
      +member_id,
      { hashedPassword: hashedPasswordVar },
      'response')
      .pipe(
        first(),
        tap((_) => {
          this.location.back();
          this.notificationService.successNotification();
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
