import {Component, OnInit, ViewEncapsulation} from '@angular/core';
import {OAuthService} from 'angular-oauth2-oidc';

@Component({
  selector: 'app-portail',
  templateUrl: './portail.component.html',
  encapsulation: ViewEncapsulation.None,
  styleUrls: ['./portail.component.css']
})
export class PortailComponent implements OnInit {

  constructor(
    public oauthService: OAuthService,
  ) { }

  ngOnInit() { }

  public login() {
    this.oauthService.initCodeFlow();
  }

}
