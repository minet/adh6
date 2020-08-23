import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CotisantRecotisationComponent } from './cotisant-recotisation.component';

describe('CotisantRecotisationComponent', () => {
  let component: CotisantRecotisationComponent;
  let fixture: ComponentFixture<CotisantRecotisationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CotisantRecotisationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CotisantRecotisationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
