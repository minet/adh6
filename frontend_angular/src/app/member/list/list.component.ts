import {CommonModule} from "@angular/common";
import {Component} from "@angular/core";
import {RouterModule} from "@angular/router";
import {map, Observable, of, shareReplay, switchMap} from "rxjs";
import {
  MemberService,
  AbstractMember,
  RoomMembersService,
  MemberFilter,
  Member,
  RoomService,
} from "../../api";
import {PaginationComponent} from "../../pagination/pagination.component";
import {SearchPage} from "../../search-page";

@Component({
  imports: [CommonModule, RouterModule, PaginationComponent],
  selector: "app-list",
  templateUrl: "./list.component.html",
})
export class ListComponent extends SearchPage<number> {
  public cachedMembers: Map<number, Observable<AbstractMember>> = new Map();
  public cachedRoomNumbers: Map<number, Observable<string>> = new Map();
  public subscriptionFilter = "";
  public subscriptionValues = Member.MembershipEnum;

  // GDPR privacy check - only show sensitive data when results are filtered down
  public get shouldShowSensitiveData(): boolean {
    return this.maxItems <= this.itemsPerPage;
  }

  constructor(
    private readonly memberService: MemberService,
    private readonly roomMemberService: RoomMembersService,
    private readonly roomService: RoomService,
  ) {
    super((terms, page) =>
      this.memberService
        .memberGet(
          this.itemsPerPage,
          (page - 1) * this.itemsPerPage,
          terms,
          this.subscriptionFilter !== ""
            ? <MemberFilter>{membership: this.subscriptionFilter}
            : undefined,
          "response",
        )
        .pipe(
          map((response) => {
            if (response.body) {
              for (const i of response.body) {
                this.cachedMembers.set(
                  +i,
                  this.memberService.memberIdGet(+i).pipe(shareReplay(1)),
                );
                this.cachedRoomNumbers.set(
                  +i,
                  this.roomMemberService.roomMemberIdGet(+i).pipe(
                    shareReplay(1),
                    switchMap((response) => {
                      if (response === undefined || response === null) {
                        return of("No room");
                      }
                      return this.roomService
                        .roomIdGet(Number(response), ["roomNumber"])
                        .pipe(map((r) => String(r.roomNumber) || "No room"));
                    }),
                  ),
                );
              }
            }
            return response;
          }),
        ),
    );
  }

  updateSubscriptionFilter(subscriptionType: string) {
    this.subscriptionFilter = subscriptionType;
    this.resetSearch();
    this.getSearchResult();
  }

  onSubscriptionFilterChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.updateSubscriptionFilter(target.value);
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }

  public getMember(id: number): Observable<AbstractMember | null> {
    return this.cachedMembers.get(id) || of(null);
  }

  public getRoomNumber(id: number | undefined): Observable<string> {
    if (id === undefined) return of("Aucune");
    return this.cachedRoomNumbers.get(id) || of("Aucune");
  }
}
