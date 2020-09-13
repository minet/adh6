import { TestBed } from '@angular/core/testing';

import { ErrorPageService } from './error-page.service';

describe('ErrorPageService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: ErrorPageService = TestBed.get(ErrorPageService);
    expect(service).toBeTruthy();
  });
});
