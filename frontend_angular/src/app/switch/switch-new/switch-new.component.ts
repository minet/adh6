import { Router } from '@angular/router';
import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { AbstractSwitch, Switch, SwitchService } from '../../api';
import { takeWhile } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-switch-new',
  templateUrl: './switch-new.component.html',
  styleUrls: ['./switch-new.component.css']
})
export class SwitchNewComponent {

  switches$: Observable<Array<AbstractSwitch>>;
  switchForm: UntypedFormGroup;
  disabled = false;
  private alive = true;

  constructor(
    private fb: UntypedFormBuilder,
    public switchService: SwitchService,
    private router: Router,
    private notificationService: NotificationService,
  ) {
    this.switchForm = this.fb.group({
      ip: ['', [Validators.required, Validators.minLength(11), Validators.maxLength(15)]],
      description: ['', Validators.required],
      community: ['', Validators.required],
    });
    this.switches$ = this.switchService.switchGet();
  }

  onSubmit() {
    const v = this.switchForm.value;
    const varSwitch: Switch = {
      description: v.description,
      ip: v.ip,
      community: v.community,
    };

    this.switchService.switchPost(varSwitch)
      .pipe(takeWhile(() => this.alive))
      .subscribe(() => {
        this.router.navigate(['/switch/search']);
        this.notificationService.successNotification();
      });
  }
}
