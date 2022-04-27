import { Component, Input, OnInit } from '@angular/core';
import { AbstractMembership, Membership, MembershipService } from '../../api';
import { Observable } from 'rxjs';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-membership-list',
  templateUrl: './membership-list.component.html'
})
export class MembershipListComponent extends SearchPage<Membership> implements OnInit {
  @Input() abstractFilterMembership: AbstractMembership = {};
  result$: Observable<Array<Membership>>;

  status_enum = ['INITIAL', 'PENDING_RULES', 'PENDING_PAYMENT_INITIAL', 'PENDING_PAYMENT', 'PENDING_PAYMENT_VALIDATION', 'COMPLETE', 'CANCELLED', 'ABORTED'];

  constructor(
    private membershipService: MembershipService,
  ) {
    super((terms, page) => this.membershipService.membershipSearch(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, this.abstractFilterMembership, 'response'));
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
    this.getSearchResult()
  }

  ngOnInit(): void {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
