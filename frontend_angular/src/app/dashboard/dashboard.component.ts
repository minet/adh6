import { Component } from '@angular/core';
import { Member } from '../api';
import { Observable } from 'rxjs';
import { SessionService } from '../session.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  public member$: Observable<Member>;
  public currentTab = "device";

  constructor(
    private sessionService: SessionService
  ) {
    this.member$ = this.sessionService.getUser();
  }
}
