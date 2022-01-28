import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MemberDeviceListComponent } from './member-device-list.component';

describe('MemberDeviceListComponent', () => {
  let component: MemberDeviceListComponent;
  let fixture: ComponentFixture<MemberDeviceListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MemberDeviceListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MemberDeviceListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
