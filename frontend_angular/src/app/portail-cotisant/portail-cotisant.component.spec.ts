import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PortailCotisantComponent } from './portail-cotisant.component';

describe('PortailCotisantComponent', () => {
  let component: PortailCotisantComponent;
  let fixture: ComponentFixture<PortailCotisantComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PortailCotisantComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PortailCotisantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
