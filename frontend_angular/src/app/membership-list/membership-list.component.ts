import { Component, OnInit } from '@angular/core';
import {Membership, MembershipService} from '../api';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import {SearchPage} from '../search-page';
import {PagingConf} from '../paging.config';

class MembershipListResponse {
  memberships?: Array<Membership>;
  page_number?: number;
  item_count?: number;
  item_per_page?: number;
}

@Component({
  selector: 'app-membership-list',
  templateUrl: './membership-list.component.html',
  styleUrls: ['./membership-list.component.sass']
})
export class MembershipListComponent extends SearchPage implements OnInit {
  result$: Observable<MembershipListResponse>;

  constructor(
    private membershipService: MembershipService,
  ) {
    super();
  }

  ngOnInit(): void {
    super.ngOnInit();
    this.result$ = this.getSearchResult((term, page) => this.fetchMemberships(term, page));
    this.result$.subscribe((result) => console.log(result));
  }

  private fetchMemberships(terms: string, page: number) {
    const n = +PagingConf.item_count;
    return this.membershipService.membershipSearch(n, (page - 1) * n, terms, undefined, 'response')
      .pipe(
        // switch to new search observable each time the term changes
        map((response) => <MembershipListResponse>{
          memberships: response.body,
          item_count: +response.headers.get('x-total-count'),
          page_number: page,
          item_per_page: n,
        }),
      );
  }
}
