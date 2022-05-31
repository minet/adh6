import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MailinglistComponent } from './mailinglist.component';
import { FormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    MailinglistComponent
  ],
  imports: [
    CommonModule,
    FormsModule
  ],
  exports: [
    MailinglistComponent
  ]
})
export class MailinglistModule { }
