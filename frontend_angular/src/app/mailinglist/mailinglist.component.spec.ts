import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MailinglistComponent } from './mailinglist.component';

describe('MailinglistComponent', () => {
  let component: MailinglistComponent;
  let fixture: ComponentFixture<MailinglistComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MailinglistComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MailinglistComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
