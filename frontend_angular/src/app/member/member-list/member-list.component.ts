import { Component, OnInit } from '@angular/core';
import { MemberService, Member } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-members',
  templateUrl: './member-list.component.html',
  styleUrls: ['./member-list.component.css']
})
export class MemberListComponent extends SearchPage<Member> implements OnInit {
  constructor(public memberService: MemberService) {
    super((terms, page) => this.memberService.memberGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, "response"));
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
