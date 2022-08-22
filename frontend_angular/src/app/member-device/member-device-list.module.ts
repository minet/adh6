import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ListComponent } from './list/list.component';
import { MacVendorComponent } from './list/mac-vendor/mac-vendor.component';
import { NewComponent } from './new/new.component';
import { ReactiveFormsModule } from '@angular/forms';
import { AbilityModule } from '@casl/angular';
import { ElementComponent } from './list/element/element.component';

@NgModule({
  declarations: [
    ListComponent,
    MacVendorComponent,
    NewComponent,
    ElementComponent,
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    AbilityModule,
  ],
  exports: [
    ListComponent,
    NewComponent
  ]
})
export class MemberDeviceModule { }
