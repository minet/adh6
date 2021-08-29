 import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {AbstractPort, ModelSwitch, Port, PortService, SwitchService} from '../api';
import {map, share} from 'rxjs/operators';

@Component({
  selector: 'app-switch-local',
  templateUrl: './switch-local.component.html',
  styleUrls: ['./switch-local.component.css']
})
export class SwitchLocalComponent implements OnInit, OnDestroy {
  switch$: Observable<ModelSwitch>;
  ports$: Observable<Array<Port>>;

  constructor(public switchService: SwitchService, public portService: PortService) {
  }

  ngOnInit() {
    this.switch$ = this.switchService.switchGet(undefined, undefined, 'Switch Local', {}).pipe(
      map((switchObjArr) => {
        const switchObj = switchObjArr[0];
        this.ports$ = this.portService.portGet(52, undefined, '', <AbstractPort>{switchObj: switchObj.id});
        return switchObj;
      }));
  }

  ngOnDestroy() {
  }

}
