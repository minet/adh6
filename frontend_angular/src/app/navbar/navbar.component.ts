import { Component } from '@angular/core';
import { SessionService } from '../session.service';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  public isMenuActive: boolean = false;

  constructor(
    public sessionService: SessionService
  ) { }

  logout() {
    this.sessionService.logout();
  }
}
