import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { AbstractPort, AbstractSwitch, PortService, SwitchService } from '../api';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-switch-local',
  templateUrl: './switch-local.component.html',
  styleUrls: ['./switch-local.component.css']
})
export class SwitchLocalComponent implements OnInit {
  switch$: Observable<AbstractSwitch>;
  ports$: Observable<Array<AbstractPort>>;

  constructor(
    private switchService: SwitchService,
    private portService: PortService
  ) { }

  ngOnInit() {
    this.switch$ = this.switchService.switchGet(undefined, undefined, 'Switch Local', {}).pipe(
      map((switchObjArr) => {
        const switchObj = switchObjArr[0];
        this.ports$ = this.portService.portGet(52, undefined, '', <AbstractPort>{ switchObj: switchObj.id });
        return switchObj;
      }));
  }
}
