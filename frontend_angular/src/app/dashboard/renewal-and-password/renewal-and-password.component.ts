import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-renewal-and-password',
  templateUrl: './renewal-and-password.component.html',
  styleUrls: ['./renewal-and-password.component.sass']
})
export class RenewalAndPasswordComponent {
  @Input() memberId: number;
  constructor() { }
}
