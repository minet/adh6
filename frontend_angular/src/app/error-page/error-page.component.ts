import {Component, OnInit} from '@angular/core';
import {ErrorPageService} from '../error-page.service';

@Component({
  selector: 'app-error-page',
  templateUrl: './error-page.component.html',
  styleUrls: ['./error-page.component.css']
})
export class ErrorPageComponent implements OnInit {
  HANDLED_ERRORS = [
    403, 500, 404
  ];
  error: any;
  constructor(private errorPageService: ErrorPageService) { }

  ngOnInit() {
    this.errorPageService.currentError.subscribe(error => this.error = error);
  }

}
