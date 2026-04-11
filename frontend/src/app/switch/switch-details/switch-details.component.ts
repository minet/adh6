import {Component, OnInit} from "@angular/core";
import {AsyncPipe} from "@angular/common";

import {Observable} from "rxjs";
import {ActivatedRoute, RouterModule} from "@angular/router";

import {AbstractSwitch, SwitchService} from "../../api";
import {PortListComponent} from "../../port/list/list.component";

@Component({
  imports: [AsyncPipe, PortListComponent, RouterModule],
  selector: "app-switch-details",
  templateUrl: "./switch-details.component.html",
  styleUrls: ["./switch-details.component.css"],
})
export class SwitchDetailsComponent implements OnInit {
  switch$!: Observable<AbstractSwitch>;
  switchId = 0;

  constructor(
    private readonly switchService: SwitchService,
    private readonly route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.switchId = +params["switch_id"];
      this.switch$ = this.switchService.switchIdGet(this.switchId);
    });
  }
}
