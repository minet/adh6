import {CommonModule} from "@angular/common";
import {Component, DestroyRef, inject} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {FormControl, ReactiveFormsModule} from "@angular/forms";
import {RouterModule} from "@angular/router";
import {
  BehaviorSubject,
  catchError,
  combineLatest,
  concat,
  map,
  Observable,
  of,
  shareReplay,
  startWith,
  switchMap,
  timer,
} from "rxjs";
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
import {ComboboxComponent, ComboboxOption} from "../../ui/combobox.component";
import {MemberSuggestionsService} from "../../ui/member-suggestions.service";

const ROOM_NONE = $localize`:@@member.list.room.none:Aucune`;

@Component({
  imports: [
    CommonModule,
    RouterModule,
    PaginationComponent,
    ReactiveFormsModule,
    ComboboxComponent,
  ],
  selector: "app-list",
  templateUrl: "./list.component.html",
})
export class ListComponent extends SearchPage<number> {
  public cachedMembers: Map<number, Observable<AbstractMember>> = new Map();
  public cachedRoomNumbers: Map<number, Observable<string>> = new Map();
  public subscriptionFilter = "";
  public subscriptionValues = Member.MembershipEnum;
  readonly memberSearch = new FormControl("", {nonNullable: true});
  private readonly suggestionFilter$ = new BehaviorSubject<
    MemberFilter | undefined
  >(undefined);
  private readonly suggestions = inject(MemberSuggestionsService);
  private readonly destroyRef = inject(DestroyRef);
  readonly suggestionState$: Observable<{
    options: ComboboxOption[];
    loading: boolean;
    unavailable: boolean;
  }> = combineLatest([
    this.memberSearch.valueChanges.pipe(startWith("")),
    this.suggestionFilter$,
  ]).pipe(
    // Clear old suggestions and cancel the old request as soon as the query changes.
    switchMap(([term, filter]) =>
      term.trim().length < 2
        ? of({options: [], loading: false, unavailable: false})
        : concat(
            of({options: [], loading: true, unavailable: false}),
            timer(300).pipe(
              switchMap(() =>
                this.suggestions.search(term, filter, this.itemsPerPage),
              ),
              map((options) => ({options, loading: false, unavailable: false})),
              catchError(() =>
                of({options: [], loading: false, unavailable: true}),
              ),
            ),
          ),
    ),
    shareReplay({bufferSize: 1, refCount: true}),
  );

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
                        return of(ROOM_NONE);
                      }
                      return this.roomService
                        .roomIdGet(Number(response), ["roomNumber"])
                        .pipe(map((r) => String(r.roomNumber) || ROOM_NONE));
                    }),
                  ),
                );
              }
            }
            return response;
          }),
        ),
    );
    this.memberSearch.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((term) => this.search(term));
  }

  updateSubscriptionFilter(subscriptionType: string) {
    this.subscriptionFilter = subscriptionType;
    this.suggestionFilter$.next(
      subscriptionType
        ? {membership: subscriptionType as MemberFilter.MembershipEnum}
        : undefined,
    );
    this.resetSearch();
    this.changePage(1);
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
    if (id === undefined) return of(ROOM_NONE);
    return this.cachedRoomNumbers.get(id) || of(ROOM_NONE);
  }
}
