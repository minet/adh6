import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AutoTroubleshootComponent } from './auto-troubleshoot.component';

describe('AutoTroubleshootComponent', () => {
  let component: AutoTroubleshootComponent;
  let fixture: ComponentFixture<AutoTroubleshootComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AutoTroubleshootComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AutoTroubleshootComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
