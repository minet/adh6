import { Component, OnInit } from '@angular/core';
import { AbstractRoom, RoomService } from '../../api';

import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-rooms',
  templateUrl: './room-list.component.html'
})

export class RoomListComponent extends SearchPage<AbstractRoom> implements OnInit {
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
