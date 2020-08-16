import { TestBed } from '@angular/core/testing';

import { AppConstantsService } from './app-constants.service';

describe('AppConstantsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: AppConstantsService = TestBed.get(AppConstantsService);
    expect(service).toBeTruthy();
  });
});
