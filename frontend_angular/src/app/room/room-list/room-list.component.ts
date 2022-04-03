import { Component, OnInit } from '@angular/core';

import { Observable } from 'rxjs';

import { Room, RoomService } from '../../api';
import { PagingConf } from '../../paging.config';

import { map } from 'rxjs/operators';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-rooms',
  templateUrl: './room-list.component.html',
  styleUrls: ['./room-list.component.css']
})

export class RoomListComponent extends SearchPage implements OnInit {
  result$: Observable<Array<Room>>;
  maxItems$: Observable<number>;
  currentPage: number = 1;

  constructor(public roomService: RoomService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.maxItems$ = this.getSearchHeader((terms) => this.roomService.roomHead(1, 0, terms, undefined, 'response').pipe(map((response) => { return (response) ? +response.headers.get('x-total-count') : 0 })))
    this.result$ = this.getSearchResult((terms, page) => this.fetchRoom(terms, page));
  }

  private fetchRoom(terms: string, page: number) {
    const n = +PagingConf.item_count;
    return this.roomService.roomGet(n, (page - 1) * n, terms);
  }

  handlePageChange(page: number) {
    this.changePage(page);
    this.currentPage = page;
  }
}
