import { Component, OnInit } from '@angular/core';
import { OAuthService } from 'angular-oauth2-oidc';
import { SessionService } from './session.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  constructor(
    private sessionService: SessionService,
    public oauthService: OAuthService,
  ) { }

  ngOnInit(): void {
    this.sessionService.checkSession();
  }
}
