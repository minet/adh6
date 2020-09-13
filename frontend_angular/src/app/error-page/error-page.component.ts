import {Component, OnInit} from '@angular/core';
import {BehaviorSubject, Subject} from 'rxjs';
import {ErrorPageService} from '../error-page.service';

@Component({
  selector: 'app-error-page',
  templateUrl: './error-page.component.html',
  styleUrls: ['./error-page.component.css']
})
export class ErrorPageComponent implements OnInit {
  error: any;
  constructor(private errorPageService: ErrorPageService) { }

  ngOnInit() {
    this.errorPageService.currentError.subscribe(error => this.error = error);
  }

}
