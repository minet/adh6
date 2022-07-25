import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NainaComponent } from './naina.component';

describe('NainaComponent', () => {
  let component: NainaComponent;
  let fixture: ComponentFixture<NainaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NainaComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NainaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
