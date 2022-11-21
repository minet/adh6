import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RoomListComponent } from './room-list/room-list.component';
import { RoomDetailsComponent } from './room-details/room-details.component';
import { RoomEditComponent } from './room-edit/room-edit.component';
import { RoomNewComponent } from './room-new/room-new.component';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { PaginationComponent } from '../pagination/pagination.component';


@NgModule({
  declarations: [
    RoomListComponent,
    RoomDetailsComponent,
    RoomEditComponent,
    RoomNewComponent,
  ],
  imports: [
    ReactiveFormsModule,
    CommonModule,
    RouterModule.forChild([
      { path: '', redirectTo: 'search', pathMatch: 'full' },
      { path: 'search', component: RoomListComponent },
      { path: 'add', component: RoomNewComponent },
      { path: 'view/:room_id', component: RoomDetailsComponent },
      { path: 'edit/:room_id', component: RoomEditComponent },
    ]),
    PaginationComponent
  ]
})
export class RoomModule { }
