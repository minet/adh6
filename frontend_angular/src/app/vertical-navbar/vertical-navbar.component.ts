import { Component } from '@angular/core';

@Component({
  selector: 'app-vertical-navbar',
  templateUrl: './vertical-navbar.component.html',
  styleUrls: ['./vertical-navbar.component.sass']
})
export class VerticalNavbarComponent {
  constructor() { }

  public activeFromUrlPath(path: string): boolean {
    return window.location.pathname.includes(path);
  }
}
