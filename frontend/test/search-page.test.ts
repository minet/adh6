import "@angular/compiler";
import {HttpHeaders, HttpResponse} from "@angular/common/http";
import {deepStrictEqual, equal} from "node:assert/strict";
import {test} from "node:test";
import {Observable, of, Subject, throwError} from "rxjs";
import {TestScheduler} from "rxjs/testing";
import {SearchPage} from "../src/app/search-page";

function response(term: string, count = 1) {
  return new HttpResponse({
    body: [term],
    headers: new HttpHeaders({"x-total-count": String(count)}),
  });
}

test("editing a subscribed search replaces results and never requests the previous text", () => {
  const scheduler = new TestScheduler(deepStrictEqual);
  scheduler.run(() => {
    const calls: {term: string; page: number}[] = [];
    const page = new SearchPage((term, number) => {
      calls.push({term, page: number});
      return of(response(term));
    });
    page.ngOnInit();
    const results: string[][] = [];
    page.result$.subscribe((items) => results.push(items));
    scheduler.schedule(() => page.changePage(3), 350);
    scheduler.schedule(() => page.search("5110"), 400);
    scheduler.schedule(() => {
      deepStrictEqual(calls, [
        {term: "", page: 1},
        {term: "", page: 3},
        {term: "5110", page: 1},
      ]);
      deepStrictEqual(results.at(-1), ["5110"]);
      equal(page.currentPage, 1);
    }, 750);
  });
});

test("editing cancels the pending request immediately and ignores its late response", () => {
  const scheduler = new TestScheduler(deepStrictEqual);
  scheduler.run(() => {
    const old = new Subject<HttpResponse<string[]>>();
    let canceled = false;
    const page = new SearchPage((term) =>
      term
        ? of(response(term, 2))
        : new Observable((subscriber) => {
            const subscription = old.subscribe(subscriber);
            return () => {
              canceled = true;
              subscription.unsubscribe();
            };
          }),
    );
    page.ngOnInit();
    const results: string[][] = [];
    page.result$.subscribe((items) => results.push(items));
    scheduler.schedule(() => page.search("new"), 350);
    scheduler.schedule(() => {
      equal(canceled, true);
      old.next(response("old", 100));
      equal(
        results.some((items) => items.includes("old")),
        false,
      );
    }, 351);
    scheduler.schedule(() => {
      deepStrictEqual(results.at(-1), ["new"]);
      equal(page.maxItems, 2);
    }, 700);
  });
});

test("multiple template subscribers share one request and searching survives HTTP errors", () => {
  const scheduler = new TestScheduler(deepStrictEqual);
  scheduler.run(() => {
    let calls = 0;
    const page = new SearchPage((term) => {
      calls++;
      return term === "broken"
        ? throwError(() => new Error("HTTP failure"))
        : of(response(term));
    });
    page.ngOnInit();
    const results: string[][] = [];
    const errors: unknown[] = [];
    page.result$.subscribe({
      next: (items) => results.push(items),
      error: (error) => errors.push(error),
    });
    page.result$.subscribe({error: (error) => errors.push(error)});
    scheduler.schedule(() => page.search("broken"), 350);
    scheduler.schedule(() => page.search("recovered"), 700);
    scheduler.schedule(() => {
      equal(calls, 3);
      deepStrictEqual(errors, []);
      deepStrictEqual(results.at(-1), ["recovered"]);
    }, 1050);
  });
});

test("refreshing filters updates existing subscriptions and invalidates cached pages", () => {
  class FilteredPage extends SearchPage<string> {
    refresh() {
      this.resetSearch();
    }
  }
  const scheduler = new TestScheduler(deepStrictEqual);
  scheduler.run(() => {
    let filter = "first";
    const calls: string[] = [];
    const page = new FilteredPage(() => {
      calls.push(filter);
      return of(response(filter));
    });
    page.ngOnInit();
    const results: string[][] = [];
    const original = page.result$;
    page.result$.subscribe((items) => results.push(items));
    scheduler.schedule(() => {
      filter = "second";
      page.refresh();
    }, 350);
    scheduler.schedule(() => {
      equal(page.result$, original);
      deepStrictEqual(results.at(-1), ["second"]);
      deepStrictEqual(calls, ["first", "second"]);
    }, 700);
  });
});

test("rapid input sends only the final text, and clearing refreshes immediately", () => {
  const scheduler = new TestScheduler(deepStrictEqual);
  scheduler.run(() => {
    const calls: {term: string; time: number}[] = [];
    const page = new SearchPage((term) => {
      calls.push({term, time: scheduler.now()});
      return of(response(term));
    });
    page.ngOnInit();
    page.result$.subscribe();
    deepStrictEqual(calls, [{term: "", time: 0}]);
    scheduler.schedule(() => page.search("d"), 10);
    scheduler.schedule(() => page.search("du"), 50);
    scheduler.schedule(() => page.search("dupont"), 100);
    scheduler.schedule(() => {
      deepStrictEqual(calls, [
        {term: "", time: 0},
        {term: "dupont", time: 350},
      ]);
      page.search("dupont ");
      equal(calls.length, 2);
      page.search("");
      deepStrictEqual(calls.at(-1), {term: "", time: 400});
    }, 400);
  });
});

test("leaving the page cancels HTTP and retry reloads the current search after an error", () => {
  let canceled = false;
  const pending = new SearchPage(
    () =>
      new Observable<HttpResponse<string[]>>(() => () => {
        canceled = true;
      }),
  );
  pending.ngOnInit();
  const subscription = pending.result$.subscribe();
  subscription.unsubscribe();
  equal(canceled, true);

  let failing = true;
  const retry = new SearchPage(() =>
    failing ? throwError(() => new Error("offline")) : of(response("retried")),
  );
  retry.ngOnInit();
  const results: string[][] = [];
  retry.result$.subscribe((items) => results.push(items));
  equal(retry.searchFailed, true);
  failing = false;
  retry.retrySearch();
  equal(retry.searchFailed, false);
  equal(retry.loading, false);
  deepStrictEqual(results.at(-1), ["retried"]);
});
