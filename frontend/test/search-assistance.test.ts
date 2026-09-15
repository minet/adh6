import "@angular/compiler";
import "@angular/localize/init";
import {
  DestroyRef,
  inject,
  Injector,
  Provider,
  runInInjectionContext,
  SimpleChange,
} from "@angular/core";
import {HttpHeaders, HttpResponse} from "@angular/common/http";
import {FormControl} from "@angular/forms";
import {deepStrictEqual, equal} from "node:assert/strict";
import {test} from "node:test";
import {firstValueFrom, Observable, of, Subscriber} from "rxjs";
import {
  MemberService,
  PortService,
  RoomMembersService,
  RoomService,
  SwitchService,
} from "../src/app/api";
import {ListComponent as MemberListComponent} from "../src/app/member/list/list.component";
import {PortListComponent} from "../src/app/port/list/list.component";
import {PaginationComponent} from "../src/app/pagination/pagination.component";
import {SearchPage} from "../src/app/search-page";
import {
  ComboboxComponent,
  ComboboxOption,
} from "../src/app/ui/combobox.component";
import {loadAllPages, loadSwitchOptions} from "../src/app/ui/entity-options";
import {MemberSuggestionsService} from "../src/app/ui/member-suggestions.service";

function context<T>(factory: () => T, providers: Provider[] = []): T {
  return runInInjectionContext(
    Injector.create({
      providers: [
        {provide: DestroyRef, useValue: {onDestroy: () => () => {}}},
        {provide: MemberService, useValue: {}},
        {provide: RoomMembersService, useValue: {}},
        {provide: RoomService, useValue: {}},
        {provide: SwitchService, useValue: {switchGet: () => of([])}},
        {provide: MemberSuggestionsService, useClass: MemberSuggestionsService},
        ...providers,
      ],
    }),
    factory,
  );
}

const pause = (milliseconds: number) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

test("search mode preserves arbitrary text and keeps editing possible during source loading/failure", () => {
  const combo = context(() => new ComboboxComponent());
  combo.mode = "search";
  combo.options = [{value: "5110", label: "5110 — Chambre double"}];
  combo.loading = true;
  combo.ngOnChanges();
  equal(combo.selection.enabled, true);
  combo.search("double");
  equal(combo.selection.value, "double");
  equal(combo.validate(new FormControl("double")), null);
  combo.onBlur();
  equal(combo.query, "double");
  combo.loading = false;
  combo.unavailable = true;
  combo.ngOnChanges();
  combo.search("autre recherche");
  equal(combo.selection.value, "autre recherche");
  equal(combo.validate(new FormControl("autre recherche")), null);
  combo.writeValue("");
  equal(combo.query, "");
});

test("choosing a search suggestion emits its identifier, not its display label", () => {
  const combo = context(() => new ComboboxComponent());
  combo.mode = "search";
  combo.options = [{value: "jdupont", label: "jdupont — Jean Dupont"}];
  let selected: ComboboxOption | undefined;
  combo.optionSelected.subscribe((option) => {
    selected = option;
  });
  combo.search("Jean");
  combo.choose(combo.options[0]);
  equal(combo.selection.value, "jdupont");
  equal(combo.query, "jdupont — Jean Dupont");
  equal(selected, combo.options[0]);
  combo.onBlur();
  equal(combo.query, "jdupont — Jean Dupont");
});

test("server-filtered suggestions are not hidden when searching by a non-displayed field", () => {
  const combo = context(() => new ComboboxComponent());
  combo.mode = "search";
  combo.filterLocally = false;
  combo.options = [{value: "jdupont", label: "jdupont — Jean Dupont"}];
  combo.search("jean@example.org");
  equal(combo.filteredOptions.length, 1);
});

test("paginated option loaders include every page and the empty final page", async () => {
  const calls: number[] = [];
  const values = await firstValueFrom(
    loadAllPages((limit, offset) => {
      calls.push(offset);
      return of([1, 2, 3, 4].slice(offset, offset + limit));
    }, 2),
  );
  deepStrictEqual(values, [1, 2, 3, 4]);
  deepStrictEqual(calls, [0, 2, 4]);
});

test("switch suggestions include descriptions and IPs and are not truncated to 100 entries", async () => {
  const calls: number[] = [];
  const service = context(
    () => inject(SwitchService),
    [
      {
        provide: SwitchService,
        useValue: {
          switchGet: (_limit: number, offset: number) => {
            calls.push(offset);
            return of(
              offset === 0
                ? Array.from({length: 100}, (_, index) => ({
                    id: index + 1,
                    description: `Switch ${index + 1}`,
                    ip: `192.0.2.${index + 1}`,
                  }))
                : [
                    {id: 101, description: "Switch 101", ip: "192.0.2.101"},
                    {description: "No ID"},
                  ],
            );
          },
        },
      },
    ],
  );
  const options = await firstValueFrom(loadSwitchOptions(service));
  equal(options.length, 101);
  equal(options[0].label, "Switch 1 : 192.0.2.1");
  equal(options[100].value, 101);
  deepStrictEqual(calls, [0, 100]);
});

test("member suggestions never request an unfiltered dataset or names for broad matches", async () => {
  let searches = 0;
  let details = 0;
  const suggestions = context(
    () => new MemberSuggestionsService(),
    [
      {
        provide: MemberService,
        useValue: {
          memberGet: () => {
            searches++;
            return of(
              new HttpResponse({
                body: [1, 2],
                headers: new HttpHeaders({"x-total-count": "50"}),
              }),
            );
          },
          memberIdGet: () => {
            details++;
            return of({username: "test"});
          },
        },
      },
    ],
  );
  deepStrictEqual(
    await firstValueFrom(suggestions.search("", undefined, 3)),
    [],
  );
  deepStrictEqual(
    await firstValueFrom(suggestions.search("a", undefined, 3)),
    [],
  );
  equal(searches, 0);
  deepStrictEqual(
    await firstValueFrom(suggestions.search("du", undefined, 3)),
    [],
  );
  equal(searches, 1);
  equal(details, 0);
});

test("member suggestions respect the result count when the total header is absent", async () => {
  let details = 0;
  const suggestions = context(
    () => new MemberSuggestionsService(),
    [
      {
        provide: MemberService,
        useValue: {
          memberGet: () => of(new HttpResponse({body: [1, 2, 3, 4]})),
          memberIdGet: () => {
            details++;
            return of({username: "test"});
          },
        },
      },
    ],
  );
  deepStrictEqual(
    await firstValueFrom(suggestions.search("dupont", undefined, 3)),
    [],
  );
  equal(details, 0);
});

test("narrow member suggestions fetch only display fields and preserve the subscription filter", async () => {
  const searches: unknown[][] = [];
  const detailCalls: unknown[][] = [];
  const suggestions = context(
    () => new MemberSuggestionsService(),
    [
      {
        provide: MemberService,
        useValue: {
          memberGet: (...args: unknown[]) => {
            searches.push(args);
            return of(
              new HttpResponse({
                body: [42],
                headers: new HttpHeaders({"x-total-count": "1"}),
              }),
            );
          },
          memberIdGet: (...args: unknown[]) => {
            detailCalls.push(args);
            return of({
              username: "jdupont",
              firstName: "Jean",
              lastName: "Dupont",
            });
          },
        },
      },
    ],
  );
  const filter = {membership: "COMPLETE" as const};
  const options = await firstValueFrom(
    suggestions.search(" Dupont ", filter, 3),
  );
  deepStrictEqual(searches[0], [4, 0, "Dupont", filter, "response"]);
  deepStrictEqual(detailCalls[0], [42, ["username", "firstName", "lastName"]]);
  deepStrictEqual(options, [
    {value: "jdupont", label: "jdupont : Jean Dupont"},
  ]);
});

test("changing a member query immediately cancels old suggestions and clears their display", async () => {
  const requests: string[] = [];
  const cancelled: string[] = [];
  const responses = new Map<string, Subscriber<ComboboxOption[]>>();
  const list = context(
    () =>
      new MemberListComponent(
        inject(MemberService),
        inject(RoomMembersService),
        inject(RoomService),
      ),
    [
      {
        provide: MemberSuggestionsService,
        useValue: {
          search: (term: string) =>
            new Observable<ComboboxOption[]>((observer) => {
              requests.push(term);
              responses.set(term, observer);
              return () => {
                cancelled.push(term);
              };
            }),
        },
      },
    ],
  );
  const states: {options: ComboboxOption[]; loading: boolean}[] = [];
  const subscription = list.suggestionState$.subscribe((state) =>
    states.push(state),
  );
  list.memberSearch.setValue("ancien");
  await pause(330);
  responses.get("ancien")!.next([{value: "ancien", label: "Ancien"}]);
  equal(states.at(-1)!.options.length, 1);
  list.memberSearch.setValue("nouveau");
  deepStrictEqual(cancelled, ["ancien"]);
  deepStrictEqual(states.at(-1)!.options, []);
  equal(states.at(-1)!.loading, true);
  await pause(330);
  deepStrictEqual(requests, ["ancien", "nouveau"]);
  responses.get("ancien")!.next([{value: "stale", label: "Stale"}]);
  deepStrictEqual(states.at(-1)!.options, []);
  responses.get("nouveau")!.next([{value: "nouveau", label: "Nouveau"}]);
  equal(states.at(-1)!.options[0].value, "nouveau");
  subscription.unsubscribe();
});

test("port filters combine room database IDs and switch IDs and reset to the first page", async () => {
  const calls: unknown[][] = [];
  const list = context(
    () =>
      new PortListComponent(
        inject(PortService),
        inject(RoomService),
        inject(SwitchService),
      ),
    [
      {
        provide: PortService,
        useValue: {
          portGet: (...args: unknown[]) => {
            calls.push(args);
            return of(
              new HttpResponse({
                body: [],
                headers: new HttpHeaders({"x-total-count": "100"}),
              }),
            );
          },
        },
      },
    ],
  );
  list.ngOnInit();
  list.changePage(3);
  list.filters.patchValue({room: 42, switchObj: 7});
  await pause(10);
  await firstValueFrom(list.result$);
  equal(list.currentPage, 1);
  equal(calls.at(-1)![1], 0);
  deepStrictEqual(calls.at(-1)![3], {room: 42, switchObj: 7});
});

test("invalid typed port filters do not fall back to an unfiltered backend request", async () => {
  const calls: unknown[][] = [];
  const list = context(
    () =>
      new PortListComponent(
        inject(PortService),
        inject(RoomService),
        inject(SwitchService),
      ),
    [
      {
        provide: PortService,
        useValue: {
          portGet: (...args: unknown[]) => {
            calls.push(args);
            return of(new HttpResponse({body: []}));
          },
        },
      },
    ],
  );
  list.switchId = 7;
  list.ngOnInit();
  const combo = context(() => new ComboboxComponent());
  combo.options = [{value: 42, label: "5110"}];
  list.filters.controls.room.addValidators((control) =>
    combo.validate(control),
  );
  combo.registerOnChange((value) => {
    if (typeof value !== "string") list.filters.controls.room.setValue(value);
  });
  combo.registerOnValidatorChange(() =>
    list.filters.controls.room.updateValueAndValidity(),
  );
  combo.search("9999");
  await pause(10);
  deepStrictEqual(await firstValueFrom(list.result$), []);
  equal(calls.length, 0);
  combo.search("");
  list.filters.controls.switchObj.setValue(99);
  await pause(10);
  await firstValueFrom(list.result$);
  deepStrictEqual(calls.at(-1)![3], {switchObj: 7});
});

test("a new text search resets the requested page and the displayed page", async () => {
  const calls: {term: string; page: number}[] = [];
  const page = new SearchPage((term, requestedPage) => {
    calls.push({term, page: requestedPage});
    return of(new HttpResponse({body: []}));
  });
  page.ngOnInit();
  page.changePage(3);
  page.search("5110");
  await firstValueFrom(page.result$);
  equal(page.currentPage, 1);
  deepStrictEqual(calls.at(-1), {term: "5110", page: 1});
});

test("pagination handles a page-only update and rebuilds ranges after filters change", () => {
  const pagination = new PaginationComponent();
  pagination.itemsPerPage = 10;
  pagination.maxItems = 100;
  pagination.ngOnChanges({maxItems: new SimpleChange(undefined, 100, true)});
  const before = [...pagination.pagesBefore];
  pagination.page = 2;
  pagination.ngOnChanges({page: new SimpleChange(1, 2, false)});
  deepStrictEqual(pagination.pagesBefore, before);
  pagination.maxItems = 40;
  pagination.ngOnChanges({maxItems: new SimpleChange(100, 40, false)});
  deepStrictEqual(pagination.pagesBefore, [2, 3]);
  deepStrictEqual(pagination.pagesAfter, [2, 3]);
  pagination.maxItems = 0;
  pagination.ngOnChanges({maxItems: new SimpleChange(40, 0, false)});
  equal(pagination.numberOfPages, 1);
});
