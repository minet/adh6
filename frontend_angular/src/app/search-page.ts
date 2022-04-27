import { BehaviorSubject, combineLatest, merge, Observable } from 'rxjs';
import { debounceTime, distinctUntilChanged, map, switchMap } from 'rxjs/operators';
import { OnInit, Directive } from '@angular/core';
import { HttpResponse } from '@angular/common/http';
import { PagingConf } from './paging.config';

@Directive()
export class SearchPage<T> implements OnInit {
  private searchTerm$ = new BehaviorSubject<string>('');
  private pageNumber$ = new BehaviorSubject<number>(1);
  private httpGetter: (term: string, page: number) => Observable<HttpResponse<Array<T>>>;
  private shouldInitSearch: boolean;
  public maxItems: number;
  public itemsPerPage: number = +PagingConf.item_count;
  public result$: Observable<Array<T>>;
  constructor(f: (term: string, page: number) => Observable<HttpResponse<Array<T>>>, shouldInitSearch?: boolean) {
    this.httpGetter = f;
    this.shouldInitSearch = (shouldInitSearch != undefined) ? shouldInitSearch : true;
  }

  ngOnInit() {
    this.changePage(1);
    if (this.shouldInitSearch) {
      this.getSearchResult();
    }
  }

  protected getSearchResult(): void {
    // Stream of terms debounced
    const termsDebounced$ = this.searchTerm$
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
      );

    // Combine terms + page and fetch the result from backend
    const result$ = combineLatest([termsDebounced$, this.pageNumber$])
      .pipe(
        switchMap(data => {
          return this.httpGetter(data[0], data[1])
            .pipe(map(response => {
              const maxItems = +response.headers.get("x-total-count");
              if (this.maxItems != maxItems) {
                this.maxItems = maxItems;
              }
              return response.body;
            }));
        }),
      );

    // When a new page is requested, emit an empty result to clear the page
    this.result$ = merge(
      result$,
      this.pageNumber$
        .pipe(
          map(() => null)
        )
    );
  }

  public search(term: string): void {
    this.searchTerm$.next(term);
  }

  public changePage(page: number): void {
    this.pageNumber$.next(page);
  }
}
