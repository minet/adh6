import { Component } from '@angular/core';
import { map, Observable, shareReplay, switchMap } from 'rxjs';
import { MemberService, AbstractMember, RoomMembersService, MemberFilter, Member, RoomService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent extends SearchPage<number> {
  public cachedMembers: Map<Number, Observable<AbstractMember>> = new Map();
  public cachedRoomNumbers: Map<Number, Observable<number>> = new Map();
  public subscriptionFilter: string = "";
  public subscriptionValues = Member.MembershipEnum;

  constructor(
    private memberService: MemberService,
    private roomMemberService: RoomMembersService,
    private roomService: RoomService
  ) {
    super((terms, page) => this.memberService.memberGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, this.subscriptionFilter !== "" ? <MemberFilter>{ membership: this.subscriptionFilter } : undefined, "response")
      .pipe(
        map(response => {
          for (let i of response.body) {
            this.cachedMembers.set(+i, this.memberService.memberIdGet(+i)
              .pipe(
                shareReplay(1)
              )
            );
            this.cachedRoomNumbers.set(+i, this.roomMemberService.roomMemberIdGet(+i)
              .pipe(
                shareReplay(1),
                switchMap((response) => this.roomService.roomIdGet(response, ["roomNumber"]).pipe(map((r) => r.roomNumber)))
              )
            );
          }
          return response
        }),
      ));
  }

  updateSubscriptionFilter(subscriptionType: string) {
    this.subscriptionFilter = subscriptionType
    this.resetSearch()
    this.getSearchResult();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }

  public getMember(id: number) {
    return this.cachedMembers.get(id)
  }

  public getRoomNumber(id: number) {
    return this.cachedRoomNumbers.get(id)
  }
}
