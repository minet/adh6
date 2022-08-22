import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RenewalAndPasswordComponent } from './renewal-and-password.component';

describe('RenewalAndPasswordComponent', () => {
  let component: RenewalAndPasswordComponent;
  let fixture: ComponentFixture<RenewalAndPasswordComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RenewalAndPasswordComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RenewalAndPasswordComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
