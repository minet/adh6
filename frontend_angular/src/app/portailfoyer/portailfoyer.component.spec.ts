import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PortailfoyerComponent } from './portailfoyer.component';

describe('PortailfoyerComponent', () => {
  let component: PortailfoyerComponent;
  let fixture: ComponentFixture<PortailfoyerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PortailfoyerComponent ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PortailfoyerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
