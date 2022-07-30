import { Component, OnInit } from '@angular/core';

import { Observable } from 'rxjs';
import { ActivatedRoute } from '@angular/router';

import { ModelSwitch, SwitchService } from '../../api';

@Component({
  selector: 'app-switch-details',
  templateUrl: './switch-details.component.html',
  styleUrls: ['./switch-details.component.css']
})
export class SwitchDetailsComponent implements OnInit {
  switch$: Observable<ModelSwitch> = new Observable();
  switchId: number = 0;

  constructor(
    private switchService: SwitchService,
    private route: ActivatedRoute
  ) { }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.switchId = +params['switch_id'];
      this.switch$ = this.switchService.switchIdGet(this.switchId);
    });
  }
}
