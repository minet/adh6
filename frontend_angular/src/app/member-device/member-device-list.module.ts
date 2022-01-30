import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ListComponent } from './list/list.component';
import { MacVendorComponent } from './list/mac-vendor/mac-vendor.component';
import { NewComponent } from './new/new.component';
import { ReactiveFormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    ListComponent,
    MacVendorComponent,
    NewComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule
  ],
  exports: [
    ListComponent,
    NewComponent
  ]
})
export class MemberDeviceModule { }
