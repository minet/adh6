import { CommonModule } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { map, Observable, shareReplay, switchMap } from 'rxjs';
import { AbstractPort, PortService, RoomService, SwitchService } from '../../api';
import { PaginationComponent } from '../../pagination/pagination.component';
import { SearchPage } from '../../search-page';

@Component({
  standalone: true,
  imports: [CommonModule, RouterModule, PaginationComponent],
  selector: 'app-port-list',
  templateUrl: './list.component.html'
})
export class PortListComponent extends SearchPage<AbstractPort> implements OnInit {
  @Input() switchId: number | undefined;
  cachedSwitchDescription: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();
  cachedRoomDescription: Map<Number, Observable<string>> = new Map<Number, Observable<string>>();

  private filter: AbstractPort = {};
  constructor(
    private portService: PortService,
    private roomService: RoomService,
    private switchService: SwitchService
  ) {
    super((terms, page) => this.portService.portGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, this.filter, ["portNumber", "room", "switchObj"], 'response')
      .pipe(
        map(response => {
          for (let p of response.body) {
            if (p.room && !this.cachedRoomDescription.has(p.room)) {
              this.cachedRoomDescription.set(p.room, this.roomService.roomGet(1, 0, undefined, {id: p.room})
                .pipe(
                  switchMap(r => this.roomService.roomRoomNumberGet(r[0])), 
                  shareReplay(1),
                  map(room => room.description)
                )
              );
            }
            if (p.switchObj && !this.cachedSwitchDescription.has(p.switchObj)) {
              this.cachedSwitchDescription.set(p.switchObj, this.switchService.switchIdGet(p.switchObj).pipe(
                shareReplay(1),
                map(s => s.description)
              ));
            }
          }
          return response;
        })
      ));
  }

  ngOnInit() {
    super.ngOnInit();
    this.filter = (this.switchId) ? <AbstractPort>{ switchObj: this.switchId } : undefined;
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}