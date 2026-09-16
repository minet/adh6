import "@angular/compiler";
import "@angular/localize/init";
import {Injector, runInInjectionContext} from "@angular/core";
import {HttpErrorResponse} from "@angular/common/http";
import {deepStrictEqual, equal, ok} from "node:assert/strict";
import {test} from "node:test";
import {Observable, of, Subject, throwError} from "rxjs";
import {
  AbstractPort,
  DiscoveredPort,
  Port,
  PortService,
  SwitchService,
} from "../src/app/api";
import {PortPickerComponent} from "../src/app/port/port-picker.component";
import {missingDiscoveredPorts} from "../src/app/port/port-discovery";
import {DialogService} from "../src/app/ui/dialog.service";
import {NotificationService} from "../src/app/notification.service";

const free: Port = {
  id: 7,
  switchObj: 1,
  portNumber: "Gi1/0/1",
  oid: "10101",
  room: null,
};

function setup(
  options: {
    ports?: (
      limit: number,
      offset: number,
      switchId: number,
    ) => Observable<AbstractPort[]>;
    discover?: () => Observable<DiscoveredPort[]>;
    confirm?: () => Promise<boolean>;
    save?: () => Observable<Port>;
    room?: number | null;
  } = {},
) {
  const assignments: {id: number; body: unknown}[] = [];
  const creations: AbstractPort[] = [];
  const confirmations: {text: string}[] = [];
  const saved: Port[] = [];
  const pages: number[] = [];
  const injector = Injector.create({
    providers: [
      {
        provide: PortService,
        useValue: {
          portGet: (
            limit: number,
            offset: number,
            _: unknown,
            filter: {switchObj: number},
          ) => {
            pages.push(offset);
            return (
              options.ports?.(limit, offset, filter.switchObj) ?? of([free])
            );
          },
          portIdRoomPatch: (id: number, body: unknown) => {
            assignments.push({id, body});
            return options.save?.() ?? of({...free, room: 42});
          },
          portPost: (body: AbstractPort) => {
            creations.push(body);
            return options.save?.() ?? of({...free, ...body, id: 8} as Port);
          },
        },
      },
      {
        provide: SwitchService,
        useValue: {
          switchIdDiscoverPortsGet: () => options.discover?.() ?? of([]),
        },
      },
      {
        provide: DialogService,
        useValue: {
          confirm: (request: {text: string}) => {
            confirmations.push(request);
            return options.confirm?.() ?? Promise.resolve(true);
          },
        },
      },
      {provide: NotificationService, useValue: {successNotification: () => {}}},
    ],
  });
  const component = runInInjectionContext(
    injector,
    () => new PortPickerComponent(),
  );
  component.switchId = 1;
  component.roomId = options.room === undefined ? 42 : options.room;
  component.saved.subscribe((port) => saved.push(port));
  component.ngOnInit();
  return {
    component,
    assignments,
    creations,
    confirmations,
    saved,
    pages,
    destroy: () => injector.destroy(),
  };
}

test("registered port assignment uses its ID and preserves its identity", async () => {
  const state = setup();
  state.component.form.controls.portKey.setValue("existing:7");
  await state.component.submit();
  deepStrictEqual(state.assignments, [
    {id: 7, body: {room: 42, expectedRoom: null}},
  ]);
  equal(state.creations.length, 0);
  equal(state.confirmations.length, 0);
  equal(state.saved.length, 1);
  state.destroy();
});

test("transfer displays the current room number and requires confirmation", async () => {
  const state = setup({
    ports: () => of([{...free, room: 9, roomObj: {roomNumber: 5110}}]),
  });
  state.component.form.controls.portKey.setValue("existing:7");
  await state.component.submit();
  ok(state.confirmations[0].text.includes("5110"));
  deepStrictEqual(state.assignments[0], {
    id: 7,
    body: {room: 42, expectedRoom: 9},
  });
  state.destroy();
});

test("cancelled transfer makes no mutation and keeps the selection", async () => {
  const state = setup({
    ports: () => of([{...free, room: 9}]),
    confirm: () => Promise.resolve(false),
  });
  state.component.form.controls.portKey.setValue("existing:7");
  await state.component.submit();
  equal(state.assignments.length, 0);
  equal(state.component.form.controls.portKey.value, "existing:7");
  equal(state.component.saving, false);
  state.destroy();
});

test("double submission does not open two confirmations or transfer twice", async () => {
  let confirm!: (value: boolean) => void;
  const state = setup({
    ports: () => of([{...free, room: 9}]),
    confirm: () =>
      new Promise((resolve) => {
        confirm = resolve;
      }),
  });
  state.component.form.controls.portKey.setValue("existing:7");
  const first = state.component.submit();
  await state.component.submit();
  equal(state.confirmations.length, 1);
  confirm(true);
  await first;
  equal(state.assignments.length, 1);
  state.destroy();
});

test("SNMP failure keeps registered ports usable and removes discovered choices", async () => {
  const state = setup({
    discover: () => throwError(() => new Error("unreachable")),
  });
  state.component.discover();
  equal(state.component.discoveryError, true);
  state.component.form.controls.portKey.setValue("discovered:10102");
  await state.component.submit();
  equal(state.creations.length, 0);
  state.component.form.controls.portKey.setValue("existing:7");
  await state.component.submit();
  equal(state.assignments.length, 1);
  state.destroy();
});

test("new port uses the discovered name and index, with no free-text fallback", async () => {
  const state = setup({
    discover: () => of([{portNumber: "Gi1/0/2", oid: "0010102"}]),
  });
  state.component.form.controls.portKey.setValue("Gi1/0/2");
  await state.component.submit();
  equal(state.creations.length, 0);
  state.component.discover();
  state.component.form.controls.portKey.setValue("discovered:10102");
  await state.component.submit();
  deepStrictEqual(state.creations, [
    {switchObj: 1, oid: "10102", portNumber: "Gi1/0/2", room: 42},
  ]);
  state.destroy();
});

test("discovery deduplicates by numeric index and excludes invalid results", () => {
  deepStrictEqual(
    missingDiscoveredPorts(
      [free],
      [
        {oid: "0010101", portNumber: "same port"},
        {oid: "10102", portNumber: "Gi1/0/2"},
        {oid: "0010102", portNumber: "same new port"},
        {oid: "Gi1/0/3", portNumber: "bad index"},
        {oid: "0", portNumber: "bad index"},
        {oid: "2147483648", portNumber: "bad index"},
        {oid: "10103", portNumber: ""},
      ],
    ),
    [{oid: "10102", portNumber: "Gi1/0/2"}],
  );
});

test("pagination includes ports beyond the first hundred and hides already attached ports", () => {
  const state = setup({
    ports: (_, offset) =>
      of(
        offset === 0
          ? Array.from({length: 100}, (_, id) => ({...free, id, room: 42}))
          : [{...free, id: 101}],
      ),
  });
  deepStrictEqual(state.pages, [0, 100]);
  equal(state.component.portOptions.length, 1);
  equal(state.component.portOptions[0].value, "existing:101");
  state.destroy();
});

test("late discovery from a previous switch cannot add choices to the new switch", () => {
  const discovery = new Subject<DiscoveredPort[]>();
  const state = setup({discover: () => discovery});
  state.component.discover();
  state.component.form.controls.switchId.setValue(2);
  discovery.next([{oid: "10102", portNumber: "old switch"}]);
  equal(state.component.discoveredPorts.length, 0);
  equal(state.component.discovering, false);
  state.destroy();
});

test("server conflict refreshes the list and requires a new selection", async () => {
  const state = setup({
    save: () => throwError(() => new HttpErrorResponse({status: 409})),
  });
  state.component.form.controls.portKey.setValue("existing:7");
  await state.component.submit();
  equal(state.saved.length, 0);
  equal(state.component.form.controls.portKey.value, null);
  equal(state.component.saving, false);
  ok(state.component.errorMessage.length > 0);
  equal(state.pages.length, 2);
  state.destroy();
});

test("switch creation screen offers only missing discovered ports", async () => {
  const state = setup({
    room: null,
    discover: () => of([{oid: "10102", portNumber: "Gi1/0/2"}]),
  });
  equal(state.component.portOptions.length, 0);
  state.component.discover();
  equal(state.component.portOptions.length, 1);
  state.component.form.controls.portKey.setValue("discovered:10102");
  await state.component.submit();
  equal(state.creations[0].room, null);
  equal(state.assignments.length, 0);
  state.destroy();
});

test("changing the target room while confirming cancels the pending transfer", async () => {
  let confirm!: (value: boolean) => void;
  const state = setup({
    ports: () => of([{...free, room: 9}]),
    confirm: () =>
      new Promise((resolve) => {
        confirm = resolve;
      }),
  });
  state.component.form.controls.portKey.setValue("existing:7");
  const submission = state.component.submit();
  state.component.roomId = 43;
  confirm(true);
  await submission;
  equal(state.assignments.length, 0);
  equal(state.creations.length, 0);
  state.destroy();
});

test("leaving the page during transfer confirmation makes no mutation", async () => {
  let confirm!: (value: boolean) => void;
  const state = setup({
    ports: () => of([{...free, room: 9}]),
    confirm: () =>
      new Promise((resolve) => {
        confirm = resolve;
      }),
  });
  state.component.form.controls.portKey.setValue("existing:7");
  const submission = state.component.submit();
  state.destroy();
  confirm(true);
  await submission;
  equal(state.assignments.length, 0);
});
