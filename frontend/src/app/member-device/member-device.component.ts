import {Component, Input, OnChanges, ViewChild} from "@angular/core";
import {AbstractDevice, AbstractMember} from "../api";
import {MemberDeviceListComponent} from "./list/list.component";
import {NewComponent} from "./new/new.component";

@Component({
  imports: [MemberDeviceListComponent, NewComponent],
  selector: "app-member-device",
  templateUrl: "./member-device.component.html",
})
export class MemberDeviceComponent implements OnChanges {
  @Input() member!: AbstractMember;

  public wiredDeviceFilter: AbstractDevice = {connectionType: "wired"};
  public wirelessDeviceFilter: AbstractDevice = {connectionType: "wireless"};

  @ViewChild(MemberDeviceListComponent) wiredList!: MemberDeviceListComponent;
  @ViewChild(MemberDeviceListComponent)
  wirelessList!: MemberDeviceListComponent;

  ngOnChanges(): void {
    if (this.wiredDeviceFilter.member === this.member.id) return;
    this.wiredDeviceFilter = {member: this.member.id, connectionType: "wired"};
    this.wirelessDeviceFilter = {
      member: this.member.id,
      connectionType: "wireless",
    };
  }

  constructor() {}
}
