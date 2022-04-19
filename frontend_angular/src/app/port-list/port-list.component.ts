import { Component, Input, OnInit } from '@angular/core';
import { AbstractPort, Port, PortService } from '../api';
import { SearchPage } from '../search-page';

@Component({
  selector: 'app-port-list',
  templateUrl: './port-list.component.html',
  styleUrls: ['./port-list.component.css']
})
export class PortListComponent extends SearchPage<Port> implements OnInit {
  @Input() switchId: number | undefined;

  private filter: AbstractPort | undefined;
  constructor(public portService: PortService) {
    super((terms, page) => this.portService.portGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, this.filter, 'response'));
  }

  ngOnInit() {
    super.ngOnInit();
    this.filter = (this.switchId) ? <AbstractPort>{ switchObj: this.switchId } : undefined;
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
