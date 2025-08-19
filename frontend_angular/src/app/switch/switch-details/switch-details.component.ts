import {Component, OnInit} from "@angular/core";
import {AsyncPipe} from "@angular/common";

import {Observable} from "rxjs";
import {ActivatedRoute} from "@angular/router";

import {AbstractSwitch, SwitchService} from "../../api";
import {PortListComponent} from "../../port/list/list.component";

@Component({
  imports: [AsyncPipe, PortListComponent],
  selector: "app-switch-details",
  templateUrl: "./switch-details.component.html",
  styleUrls: ["./switch-details.component.css"],
})
export class SwitchDetailsComponent implements OnInit {
  switch$: Observable<AbstractSwitch>;
  switchId: number = 0;

  constructor(
    private switchService: SwitchService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.switchId = +params["switch_id"];
      this.switch$ = this.switchService.switchIdGet(this.switchId);
    });
  }
}
