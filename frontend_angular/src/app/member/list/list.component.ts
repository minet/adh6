import { Component, OnInit } from '@angular/core';
import { map, Observable, shareReplay } from 'rxjs';
import { MemberService, AbstractMember, RoomMembersService } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent extends SearchPage<number> implements OnInit {
  public cachedMembers: Map<Number, Observable<AbstractMember>> = new Map();
  public cachedRoomNumbers: Map<Number, Observable<number>> = new Map();

  constructor(
    private memberService: MemberService,
    private roomMemberService: RoomMembersService
  ) {
    super((terms, page) => this.memberService.memberGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, "response")
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
                shareReplay(1)
              )
            );
          }
          return response
        }),
      ));
  }
  //  
  ngOnInit() {
    super.ngOnInit();
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
