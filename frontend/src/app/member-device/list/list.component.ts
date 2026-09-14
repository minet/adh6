import {Component, Input} from "@angular/core";
import {AbstractDevice, DeviceService, Device} from "../../api";
import {SearchPage} from "../../search-page";
import {CommonModule, AsyncPipe} from "@angular/common";
import {ElementComponent} from "./element/element.component";

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
      this.deviceService.deviceGet(
        this.itemsPerPage,
        (page - 1) * this.itemsPerPage,
        {
          terms: terms,
          member: this.abstractDeviceFilter.member,
          connectionType: this.abstractDeviceFilter.connectionType,
        },
        [
          "id",
          "mac",
          "ipv4Address",
          "ipv6Address",
          "connectionType",
          "member",
          "name",
          "wifiPassword",
          "vendor",
        ] as any,
        "response",
      ),
    );
  }

  updateSearch() {
    this.getSearchResult();
  }
}
