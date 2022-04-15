import { Component, OnInit } from '@angular/core';

import { Observable } from 'rxjs';


import { MemberService, Member } from '../../api';
import { PagingConf } from '../../paging.config';

import { map } from 'rxjs/operators';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-members',
  templateUrl: './member-list.component.html',
  styleUrls: ['./member-list.component.css']
})
export class MemberListComponent extends SearchPage implements OnInit {
  maxItems$: Observable<number>;
  result$: Observable<Array<Member>>;

  constructor(public memberService: MemberService) {
    super();
  }

  ngOnInit() {
    super.ngOnInit();
    this.maxItems$ = this.getSearchResult((term, _) => this.memberService.memberHead(1, 0, (term) ? term : undefined, undefined, 'response').pipe(map((response) => { return (response) ? +response.headers.get('x-total-count') : 0 })))
    this.result$ = this.getSearchResult((terms, page) => this.fetchMembers((terms) ? terms : undefined, page));
  }

  private fetchMembers(terms: string, page: number) {
    const n = +PagingConf.item_count;
    return this.memberService.memberGet(n, (page - 1) * n, terms);
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
