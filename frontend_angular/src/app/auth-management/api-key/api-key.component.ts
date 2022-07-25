import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import Swal from 'sweetalert2';
import { ApiKey, AuthenticationService, Body2, Role } from '../../api';

@Component({
  selector: 'app-api-key',
  templateUrl: './api-key.component.html',
  styleUrls: ['./api-key.component.sass']
})
export class ApiKeyComponent implements OnInit {
  public roleKeys = Object.values(Role);
  public result$: Observable<ApiKey[]>;
  public apiKey: string = "";
  public login: string = "";
  public roles: string[] = [];

  constructor(
    private authenticationService: AuthenticationService
  ) { }

  ngOnInit(): void {
    this.result$ = this.authenticationService.apiKeysGet();
  }
  public submit(): void {
    if (this.roles.length === 0 || this.login === "") return;

    this.authenticationService.apiKeysPost(<Body2>{
      login: this.login,
      roles: this.roles
    }).subscribe((res) => this.apiKey = res);
  }

  public delete(id: number): void {
    this.authenticationService.apiKeysIdDelete(id).subscribe(() => Swal.fire({ 'title': 'Clef supprimée' }))
  }
}
