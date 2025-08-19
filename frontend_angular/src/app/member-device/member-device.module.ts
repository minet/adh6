import {NgModule} from "@angular/core";
import {CommonModule} from "@angular/common";
import {NewComponent} from "./new/new.component";
import {ReactiveFormsModule} from "@angular/forms";
import {AblePipe} from "@casl/angular";
import {ElementComponent} from "./list/element/element.component";
import {MemberDeviceListComponent} from "./list/list.component";
import {MemberDeviceComponent} from "./member-device.component";
import {AutoTroubleshootComponent} from "./auto-troubleshoot/auto-troubleshoot.component";

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    AblePipe,
    NewComponent,
    ElementComponent,
    MemberDeviceListComponent,
    AutoTroubleshootComponent,
    MemberDeviceComponent,
  ],
  exports: [MemberDeviceComponent],
})
export class MemberDeviceModule {}
