import { Component, OnInit } from '@angular/core';
import { concatMap, forkJoin, map, Observable, shareReplay } from 'rxjs';
import { AbstractRoom, Room, RoomService } from '../../api';

import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-rooms',
  templateUrl: './room-list.component.html'
})

export class RoomListComponent extends SearchPage<number> implements OnInit {
  public cachedRoom$: Map<number, Observable<AbstractRoom>> = new Map();
  constructor(public roomService: RoomService) {
    super((terms, page) => this.roomService.roomGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, "response")
      .pipe(map(roomNumbers => {
        roomNumbers.body.forEach(r => {
          if (!this.cachedRoom$.has(r)) {
            this.cachedRoom$.set(r, this.roomService.roomRoomNumberGet(r, ["description", "vlan"]).pipe(shareReplay(1)))
          }
        });
        return roomNumbers;
      })));
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
