import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import Swal from 'sweetalert2';
import { ApiKey, ApiKeysGetRequest, AuthenticationService, Role } from '../../api';

@Component({
  selector: 'app-api-key',
  templateUrl: './api-key.component.html',
  styleUrls: ['./api-key.component.sass']
})
export class ApiKeyComponent implements OnInit {
  public roleKeys = Object.values(Role);
  public result$: Observable<ApiKey[]>;
  public login: string = "";
  public roles: string[] = [];

  constructor(
    private authenticationService: AuthenticationService
  ) { }

  ngOnInit(): void {
    this.refreshApi();
  }

  public submit(): void {
    if (this.roles.length === 0 || this.login === "") return;

    this.authenticationService.apiKeysPost(<ApiKeysGetRequest>{
      login: this.login,
      roles: this.roles
    }).subscribe((res) => Swal.fire({ 'title': 'Clé d\'API', text: res }).then(() => this.refreshApi()));
  }

  private refreshApi() {
    this.result$ = this.authenticationService.apiKeysGet();
  }

  public delete(id: number): void {
    this.authenticationService.apiKeysIdDelete(id).subscribe(() => this.refreshApi())
  }
}
