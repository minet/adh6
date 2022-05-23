import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { map, Observable } from 'rxjs';

@Component({
  selector: 'app-error-page',
  templateUrl: './error-page.component.html',
  styleUrls: ['./error-page.component.css']
})
export class ErrorPageComponent {
  HANDLED_ERRORS = [
    403, 404, 500
  ];
  error$: Observable<number>;
  constructor(
    private route: ActivatedRoute
  ) {
    this.error$ = this.route.params.pipe(
      map((params) => params["error_id"])
    );
  }
}
