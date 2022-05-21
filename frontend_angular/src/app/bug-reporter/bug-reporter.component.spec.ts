import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BugReporterComponent } from './bug-reporter.component';

describe('BugReporterComponent', () => {
  let component: BugReporterComponent;
  let fixture: ComponentFixture<BugReporterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BugReporterComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BugReporterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
