import {HttpResponse} from "@angular/common/http";
import {Directive, OnInit} from "@angular/core";
import {BehaviorSubject, defer, Observable, of, timer} from "rxjs";
import {
  catchError,
  filter,
  map,
  shareReplay,
  startWith,
  switchMap,
} from "rxjs/operators";
import {PagingConf} from "./paging.config";

interface SearchRequest {
  term: string;
  page: number;
  enabled: boolean;
  delay: number;
}

@Directive()
export class SearchPage<T> implements OnInit {
  private readonly request$ = new BehaviorSubject<SearchRequest>({
    term: "",
    page: 1,
    enabled: false,
    delay: 0,
  });
  public maxItems = 0;
  public currentPage = 1;
  public itemsPerPage: number = +PagingConf.item_count;
  public loading = false;
  public searchFailed = false;
  public readonly result$: Observable<T[]>;

  constructor(
    private readonly httpGetter: (
      term: string,
      page: number,
    ) => Observable<HttpResponse<T[]>>,
    private readonly shouldInitSearch = true,
  ) {
    this.result$ = this.request$.pipe(
      filter((request) => request.enabled),
      // Cancel both the debounce and HTTP request as soon as the input changes.
      // Text and page are emitted together, so page 1 never uses the old text.
      switchMap((request) => {
        this.loading = true;
        this.searchFailed = false;
        this.maxItems = 0;
        const ready$ = request.delay ? timer(request.delay) : of(0);
        return ready$.pipe(
          switchMap(() =>
            defer(() => this.httpGetter(request.term, request.page)),
          ),
          map((response) => {
            const items = response.body ?? [];
            const count = Number(
              response.headers.get("x-total-count") ?? items.length,
            );
            this.maxItems =
              Number.isFinite(count) && count >= 0 ? count : items.length;
            this.loading = false;
            return items;
          }),
          // Keep the outer search alive so the next edit can recover from errors.
          catchError(() => {
            this.loading = false;
            this.searchFailed = true;
            return of([] as T[]);
          }),
          // Clear obsolete rows while waiting for the new query.
          startWith([] as T[]),
        );
      }),
      shareReplay({bufferSize: 1, refCount: true}),
    );
  }

  ngOnInit(): void {
    if (this.shouldInitSearch) this.getSearchResult();
  }

  protected getSearchResult(): void {
    this.request$.next({...this.request$.value, enabled: true, delay: 0});
  }

  public resetSearch(): void {
    this.currentPage = 1;
    this.request$.next({
      ...this.request$.value,
      page: 1,
      enabled: true,
      delay: 0,
    });
  }

  public retrySearch(): void {
    this.getSearchResult();
  }

  public search(term: string): void {
    const normalized = term.trim();
    if (
      normalized === this.request$.value.term &&
      this.request$.value.enabled &&
      !this.searchFailed
    )
      return;
    this.currentPage = 1;
    this.request$.next({
      term: normalized,
      page: 1,
      enabled: true,
      delay: normalized ? 250 : 0,
    });
  }

  public changePage(page: number): void {
    if (
      !Number.isInteger(page) ||
      page < 1 ||
      page === this.request$.value.page
    )
      return;
    this.currentPage = page;
    this.request$.next({...this.request$.value, page, delay: 0});
  }
}
