import { Component, OnInit } from '@angular/core';
import { AbstractSwitch, SwitchService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-switch-list',
  templateUrl: './switch-list.component.html',
  styleUrls: ['./switch-list.component.css']
})
export class SwitchListComponent extends SearchPage<AbstractSwitch> implements OnInit {
  constructor(public switchService: SwitchService) {
    super((terms, page) => this.switchService.switchGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, ["ip", "description"], "response"));
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
