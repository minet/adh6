import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PortailComponent } from './portail.component';

describe('PortailComponent', () => {
  let component: PortailComponent;
  let fixture: ComponentFixture<PortailComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PortailComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PortailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
