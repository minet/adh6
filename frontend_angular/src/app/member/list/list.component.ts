import { Component, OnInit } from '@angular/core';
import { MemberService, Member } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent extends SearchPage<Member> implements OnInit {
  constructor(
    public memberService: MemberService,
  ) {
    super((terms, page) => this.memberService.memberGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, ["username", "firstName", "lastName", "roomNumber"], undefined, undefined, undefined, undefined, "response"));
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
