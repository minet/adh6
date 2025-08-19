import {Component, OnInit} from "@angular/core";
import {Observable} from "rxjs";
import {AbstractPort, AbstractSwitch, PortService, SwitchService} from "../api";
import {map} from "rxjs/operators";
import {CommonModule} from "@angular/common";
import {RouterModule} from "@angular/router";

@Component({
  imports: [CommonModule, RouterModule],
  selector: "app-switch-local",
  template: `
    <style>
      area {
        cursor: pointer;
      }
      img {
        width: auto !important;
        height: auto !important;
      }
    </style>
    <h1 class="title is-1">Switch Local</h1>
    <div class="has-text-center">
      <div>
        <p><strong>Adresse IP:</strong> {{ (switch$ | async)?.ip }}</p>
        @if (ports$ | async; as ports) {
          <div>
            <map name="plan-local">
              @for (portResult of ports; track portResult) {
                @if (
                  portResult.id >= 16 &&
                  portResult.id <= 24 &&
                  portResult.id % 2 === 0
                ) {
                  <area
                    coords="{{ 45 + (70 * (portResult.id - 16)) / 2 }},186,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port {{ portResult.id }}" />
                }
                @if (
                  portResult.id >= 15 &&
                  portResult.id <= 23 &&
                  portResult.id % 2 === 1
                ) {
                  <area
                    coords="{{ 31 + (70 * (portResult.id - 15)) / 2 }},215,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port {{ portResult.id }}" />
                }
                @if (portResult.id === 3) {
                  <area
                    coords="293,411,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 3" />
                }
                @if (portResult.id === 4) {
                  <area
                    coords="255,445,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 4" />
                }
                @if (portResult.id === 5) {
                  <area
                    coords="245,486,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 5" />
                }
                @if (portResult.id === 6) {
                  <area
                    coords="243,526,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 6" />
                }
                @if (portResult.id === 7) {
                  <area
                    coords="243,565,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 7" />
                }
                @if (portResult.id === 8) {
                  <area
                    coords="246,607,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 8" />
                }
                @if (portResult.id === 9) {
                  <area
                    coords="254,647,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 9" />
                }
                @if (portResult.id === 10) {
                  <area
                    coords="290,670,15"
                    [routerLink]="[
                      '/port',
                      portResult.switchObj,
                      portResult.id,
                    ]"
                    shape="circle"
                    title="Port 10" />
                }
              }
            </map>
            <img src="assets/plan-local.png" usemap="#plan-local" />
          </div>
        }
      </div>
    </div>
  `,
})
export class SwitchLocalComponent implements OnInit {
  switch$: Observable<AbstractSwitch>;
  ports$: Observable<AbstractPort[]>;

  constructor(
    private readonly switchService: SwitchService,
    private readonly portService: PortService,
  ) {}

  ngOnInit() {
    this.switch$ = this.switchService
      .switchGet(undefined, undefined, "Switch Local", {})
      .pipe(
        map((switchObjArr) => {
          const switchObj = switchObjArr[0];
          this.ports$ = this.portService.portGet(52, undefined, "", <
            AbstractPort
          >{switchObj: switchObj.id});
          return switchObj;
        }),
      );
  }
}
