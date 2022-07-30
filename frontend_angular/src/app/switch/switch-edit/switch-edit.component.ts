import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SwitchService } from '../../api';

@Component({
  selector: 'app-switch-edit',
  templateUrl: './switch-edit.component.html',
  styleUrls: ['./switch-edit.component.css']
})
export class SwitchEditComponent {
  switchForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public switchService: SwitchService,
  ) {
    this.switchForm = this.fb.group({
      ip: ['', [Validators.required, Validators.minLength(11), Validators.maxLength(15)]],
    });
  }
}
