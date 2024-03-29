import { Component, OnInit } from '@angular/core';
import { AbstractControl, ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize, map } from 'rxjs/operators';
import { MemberService } from '../api';
import { md4 } from 'hash-wasm';
import { CommonModule, Location } from '@angular/common';
import { NotificationService } from '../notification.service';

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
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  selector: 'app-member-password-edit',
  templateUrl: './member-password-edit.component.html'
})
export class MemberPasswordEditComponent implements OnInit {
  public showPassword: boolean = false;
  public showConfirmPassword: boolean = false;

  constructor(
    private fb: UntypedFormBuilder,
    private notificationService: NotificationService,
    private router: Router,
    private route: ActivatedRoute,
    private memberService: MemberService,
    private location: Location
  ) { }

  disabled = false;
  memberPassword: UntypedFormGroup;

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
      this.route.paramMap.pipe(
        map(params => {
          const member_id = +params.get('member_id');
          console.log(+params.get('creation') === 1);
          this.updatePasswordOfUser(member_id, hashedPassword, +params.get('creation') === 1)
        }),
        finalize(() => this.disabled = false)
      )
        .subscribe((_) => {
        }
        );
    });
  }

  private updatePasswordOfUser(member_id: number, hashedPasswordVar: string, creation: boolean) {
    return this.memberService.memberIdPasswordPut(+member_id, { hashedPassword: hashedPasswordVar }, 'response')
      .subscribe((_) => {
        this.notificationService.successNotification();
        if (!creation) {
          this.location.back();
        } else {
          this.router.navigate(['/member/view', member_id])
        }
      })
  }
}
