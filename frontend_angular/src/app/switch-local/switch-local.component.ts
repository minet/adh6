import {Component, OnDestroy, OnInit} from '@angular/core';
import {Observable} from 'rxjs';
import {SwitchService} from '../api';
import {ModelSwitch} from '../api';
import {Port} from '../api';
import {PortService} from '../api';

@Component({
  selector: 'app-switch-local',
  templateUrl: './switch-local.component.html',
  styleUrls: ['./switch-local.component.css']
})
export class SwitchLocalComponent implements OnInit, OnDestroy {

  switch$: Observable<ModelSwitch>;
  ports$: Observable<Array<Port>>;
  switchID = 1;

  constructor(public switchService: SwitchService, public portService: PortService) {
  }

  ngOnInit() {
    this.switchID = 1;
    this.switch$ = this.switchService.switchSwitchIDGet(this.switchID);
    this.ports$ = this.portService.portGet(undefined, undefined, this.switchID);
  }

  ngOnDestroy() {
  }

}
