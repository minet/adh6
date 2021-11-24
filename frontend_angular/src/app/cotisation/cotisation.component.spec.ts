import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CotisationComponent } from './cotisation.component';

describe('CotisationComponent', () => {
  let component: CotisationComponent;
  let fixture: ComponentFixture<CotisationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CotisationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CotisationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
