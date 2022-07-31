import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthenticationService, RoleMapping, Role, RoleGetRequest } from '../../api';

@Component({
  selector: 'app-naina',
  templateUrl: './naina.component.html',
  styleUrls: ['./naina.component.sass']
})
export class NainaComponent implements OnInit {
  public result$: Observable<RoleMapping[]>;
  public login = "";

  constructor(
    private authenticationService: AuthenticationService
  ) { }

  ngOnInit(): void {
    this.result$ = this.authenticationService.roleGet('user');
  }

  public newNainA(): void {
    this.authenticationService.rolePost(<RoleGetRequest>{
      identifier: this.login,
      roles: [
        Role.Adminread,
        Role.Adminwrite,
        Role.Networkread,
        Role.Networkwrite
      ],
      auth: 'user',
    }).subscribe();
  }
}
