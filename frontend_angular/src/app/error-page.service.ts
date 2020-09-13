import { Injectable } from '@angular/core';
import {BehaviorSubject, Subject} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ErrorPageService {
  hasError = new Subject<boolean>();
  private errorSource = new BehaviorSubject<any>(null);
  currentError = this.errorSource.asObservable();

  constructor() { }

  show(errorResponse) {
    this.hasError.next(true);
    this.errorSource.next(errorResponse);
  }

  hide() {
    this.hasError.next(false);
  }
}
