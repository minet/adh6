import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';

import { Member, MemberBody } from '../../../api';
import { CommonModule } from '@angular/common';

interface MemberEditForm {
  firstName: FormControl<string>;
  lastName: FormControl<string>;
  username: FormControl<string>;
  email: FormControl<string>;
  roomNumber: FormControl<number>;
}

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  selector: 'app-form',
  templateUrl: './form.component.html'
})
export class FormComponent implements OnInit {
  @Input() member: Member | undefined;
  @Input() roomNumber: number | undefined;
  @Output() newMember: EventEmitter<{member: MemberBody, room: number}> = new EventEmitter();

  public memberEdit: FormGroup<MemberEditForm>;

  constructor() {
    this.memberEdit = new FormGroup<MemberEditForm>({
      firstName: new FormControl(),
      lastName: new FormControl(),
      username: new FormControl(),
      email: new FormControl(),
      roomNumber: new FormControl(this.roomNumber),
    });
  }

  ngOnInit() { this.memberEdit.patchValue(this.member); }

  onSubmit() {
    const v = this.memberEdit.value;
    this.newMember.emit({member: {
      mail: v.email,
      firstName: v.firstName,
      lastName: v.lastName,
      username: v.username,
    }, room: v.roomNumber});
  }
}
