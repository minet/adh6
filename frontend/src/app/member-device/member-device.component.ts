import {Component, Input, ViewChild} from "@angular/core";
import {AbstractDevice, AbstractMember} from "../api";
import {MemberDeviceListComponent} from "./list/list.component";
import {NewComponent} from "./new/new.component";

@Component({
  imports: [MemberDeviceListComponent, NewComponent],
  selector: "app-member-device",
  templateUrl: "./member-device.component.html",
})
export class MemberDeviceComponent {
  @Input() member!: AbstractMember;

  @ViewChild(MemberDeviceListComponent) wiredList!: MemberDeviceListComponent;
  @ViewChild(MemberDeviceListComponent)
  wirelessList!: MemberDeviceListComponent;

  get wiredDeviceFilter(): AbstractDevice {
    return {
      member: this.member.id,
      connectionType: "wired",
    };
  }

  get wirelessDeviceFilter(): AbstractDevice {
    return {
      member: this.member.id,
      connectionType: "wireless",
    };
  }

  constructor() {}
}
