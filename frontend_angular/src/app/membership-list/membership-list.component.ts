import {Component, Input, OnInit} from '@angular/core';
import {AbstractMembership, Membership, MembershipService} from '../api';
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
  @Input() abstractFilterMembership: AbstractMembership = {};
  result$: Observable<MembershipListResponse>;

  status_enum = ['INITIAL', 'PENDING_RULES', 'PENDING_PAYMENT_INITIAL', 'PENDING_PAYMENT', 'PENDING_PAYMENT_VALIDATION', 'COMPLETE', 'CANCELLED', 'ABORTED'];

  constructor(
    private membershipService: MembershipService,
  ) {
    super();
  }

  redirectLink(status: AbstractMembership.StatusEnum): string {
    switch (status) {
      case 'INITIAL':
        return '/membership'
      case 'PENDING_RULES':
        return '/charter';
      case 'PENDING_PAYMENT_INITIAL':
        break
      case 'PENDING_PAYMENT':
        break
      case 'PENDING_PAYMENT_VALIDATION':
        break
      case 'COMPLETE':
        break
    }
    return "";
}

  replaceUnderscoreStatus(status: string, replaceValue: string): string {
    return status.replace("_", replaceValue).replace("_", replaceValue);
  }

  updateStatusFilter(status: string): void {
    if (this.replaceUnderscoreStatus(status, "") in AbstractMembership.StatusEnum) {
      this.abstractFilterMembership.status = status as AbstractMembership.StatusEnum;
    } else {
      delete this.abstractFilterMembership.status;
    }
    console.log(this.abstractFilterMembership);
    this.updateSearch()
  }
  updateSearch(): void {
    this.result$ = this.getSearchResult((term, page) => this.fetchMemberships(term, page));
  }

  ngOnInit(): void {
    super.ngOnInit();
    this.updateSearch()
  }

  private fetchMemberships(terms: string, page: number) {
    const n = +PagingConf.item_count;
    return this.membershipService.membershipSearch(n, (page - 1) * n, terms, this.abstractFilterMembership, 'response')
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
