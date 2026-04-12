import {Component, Input} from "@angular/core";
import {Observable} from "rxjs";
import {AbstractDevice, DeviceFilter, DeviceService, Device} from "../../api";
import {SearchPage} from "../../search-page";
import {CommonModule, AsyncPipe} from "@angular/common";
import {ElementComponent} from "./element/element.component";
import {HttpResponse} from "@angular/common/http";

@Component({
  imports: [CommonModule, AsyncPipe, ElementComponent],
  selector: "app-member-device-list",
  templateUrl: "./list.component.html",
  styleUrls: ["./list.component.css"],
})
export class MemberDeviceListComponent extends SearchPage<Device> {
  @Input() abstractDeviceFilter: AbstractDevice = {};

  constructor(public deviceService: DeviceService) {
    super((terms, page) =>
      (this.deviceService
        .deviceGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          <DeviceFilter>{
            terms: terms,
            member: this.abstractDeviceFilter.member,
            connectionType: this.abstractDeviceFilter.connectionType,
          },
          ["id", "mac", "ipv4Address", "ipv6Address", "connectionType", "member", "name", "wifiPassword", "vendor", "mab"] as any,
          "response",
        ) as Observable<HttpResponse<Device[]>>)
    );
  }

  updateSearch() {
    this.getSearchResult();
  }
}
