import { Component, OnInit } from '@angular/core';
import { Room, RoomService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-rooms',
  templateUrl: './room-list.component.html',
  styleUrls: ['./room-list.component.css']
})

export class RoomListComponent extends SearchPage<Room> implements OnInit {
  constructor(public roomService: RoomService) {
    super((terms, page) => this.roomService.roomGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, undefined, "response"));
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
