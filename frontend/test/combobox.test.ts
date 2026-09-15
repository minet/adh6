import "@angular/compiler";
import "@angular/localize/init";
import {DestroyRef, Injector, runInInjectionContext} from "@angular/core";
import {FormControl} from "@angular/forms";
import {deepStrictEqual, equal} from "node:assert/strict";
import {test} from "node:test";
import {of, throwError} from "rxjs";
import {AbstractRoom, RoomService} from "../src/app/api";
import {ComboboxComponent} from "../src/app/ui/combobox.component";
import {RoomSelectComponent} from "../src/app/ui/room-select.component";

function create<T>(
  factory: () => T,
  roomGet = () => of<AbstractRoom[]>([]),
): T {
  const injector = Injector.create({
    providers: [
      {provide: DestroyRef, useValue: {onDestroy: () => () => {}}},
      {provide: RoomService, useValue: {roomGet}},
    ],
  });
  return runInInjectionContext(injector, factory);
}

test("combobox validates supplied values without coercing numbers to strings", () => {
  const combo = create(() => new ComboboxComponent());
  combo.options = [
    {value: 42, label: "5110"},
    {value: "wifi", label: "Wi-Fi"},
  ];
  equal(combo.validate(new FormControl(42)), null);
  equal(combo.validate(new FormControl("wifi")), null);
  equal(combo.validate(new FormControl(null)), null);
  deepStrictEqual(combo.validate(new FormControl("42")), {invalidOption: true});
  deepStrictEqual(combo.validate(new FormControl(999)), {invalidOption: true});
});

test("combobox propagates changes and touched state, but not programmatic writes", () => {
  const combo = create(() => new ComboboxComponent());
  const changes: unknown[] = [];
  let touched = false;
  combo.registerOnChange((value) => changes.push(value));
  combo.registerOnTouched(() => {
    touched = true;
  });
  combo.writeValue(42);
  equal(combo.selection.value, 42);
  deepStrictEqual(changes, []);
  combo.selection.setValue("wifi");
  combo.selection.setValue(null);
  combo.onTouched();
  deepStrictEqual(changes, ["wifi", null]);
  equal(touched, true);
});

test("combobox revalidates changed options and blocks loading or failed sources", () => {
  const combo = create(() => new ComboboxComponent());
  let validations = 0;
  combo.registerOnValidatorChange(() => validations++);
  combo.loading = true;
  combo.ngOnChanges();
  equal(combo.selection.disabled, true);
  deepStrictEqual(combo.validate(new FormControl(null)), {
    optionsUnavailable: true,
  });
  combo.loading = false;
  combo.ngOnChanges();
  equal(combo.selection.enabled, true);
  combo.setDisabledState(true);
  combo.ngOnChanges();
  equal(combo.selection.disabled, true);
  combo.setDisabledState(false);
  combo.unavailable = true;
  combo.ngOnChanges();
  equal(combo.selection.disabled, true);
  equal(validations, 4);
});

test("typing filters labels and only accepts an exact existing option", () => {
  const combo = create(() => new ComboboxComponent());
  combo.options = [
    {value: 42, label: "5110"},
    {value: 43, label: "5111"},
    {value: 44, label: "6120"},
  ];
  combo.search("511");
  equal(combo.query, "511");
  equal(combo.open, true);
  deepStrictEqual(
    combo.filteredOptions.map((option) => option.value),
    [42, 43],
  );
  equal(combo.selection.value, null);
  deepStrictEqual(combo.validate(new FormControl(null)), {invalidOption: true});
  combo.search("5110");
  equal(combo.selection.value, 42);
  equal(combo.validate(new FormControl(42)), null);
  combo.search("9999");
  equal(combo.selection.value, null);
  deepStrictEqual(combo.filteredOptions, []);
  combo.onBlur();
  equal(combo.query, "9999");
  deepStrictEqual(combo.validate(new FormControl(null)), {invalidOption: true});
  combo.search("");
  equal(combo.validate(new FormControl(null)), null);
  equal(combo.filteredOptions.length, 3);
});

test("typing supports case-insensitive labels but cannot resolve ambiguous labels", () => {
  const combo = create(() => new ComboboxComponent());
  combo.options = [{value: "wifi", label: "Wi-Fi"}];
  combo.search(" wi-fi ");
  equal(combo.selection.value, "wifi");
  combo.onBlur();
  equal(combo.query, "Wi-Fi");
  combo.options = [
    {value: 1, label: "Double"},
    {value: 2, label: "Double"},
  ];
  combo.search("Double");
  equal(combo.selection.value, null);
  deepStrictEqual(combo.validate(new FormControl(null)), {invalidOption: true});
  combo.choose(combo.options[1]);
  equal(combo.selection.value, 2);
  equal(combo.validate(new FormControl(2)), null);
});

test("arrows navigate filtered suggestions and Enter selects without submitting", () => {
  const combo = create(() => new ComboboxComponent());
  combo.options = [
    {value: 1, label: "5110"},
    {value: 2, label: "5111"},
    {value: 3, label: "6120"},
  ];
  let prevented = 0;
  const press = (key: string) =>
    combo.onKeydown({
      key,
      preventDefault: () => {
        prevented++;
      },
    });
  combo.search("511");
  press("ArrowDown");
  equal(combo.activeIndex, 1);
  press("Enter");
  equal(combo.selection.value, 2);
  equal(combo.query, "5111");
  equal(combo.open, false);
  equal(prevented, 2);
  press("ArrowUp");
  equal(combo.open, true);
  equal(combo.activeIndex, 2);
  press("Escape");
  equal(combo.open, false);
  combo.search("9999");
  press("ArrowDown");
  press("Enter");
  equal(combo.activeIndex, -1);
  equal(combo.selection.value, null);
});

test("programmatic values are displayed after async options arrive, without emitting changes", () => {
  const combo = create(() => new ComboboxComponent());
  const changes: unknown[] = [];
  combo.registerOnChange((value) => changes.push(value));
  combo.writeValue(42);
  combo.options = [{value: 42, label: "5110"}];
  combo.ngOnChanges();
  equal(combo.query, "5110");
  deepStrictEqual(changes, []);
  combo.writeValue(null);
  equal(combo.query, "");
  equal(combo.fieldId !== create(() => new ComboboxComponent()).fieldId, true);
});

test("disabled combobox cannot be edited or selected", () => {
  const combo = create(() => new ComboboxComponent());
  combo.options = [{value: 42, label: "5110"}];
  combo.setDisabledState(true);
  combo.search("5110");
  combo.choose(combo.options[0]);
  combo.openOptions();
  equal(combo.selection.value, null);
  equal(combo.query, "");
  equal(combo.open, false);
});

test("room adapter loads every page, sorts numbers and preserves the selected value", () => {
  const firstPage = Array.from({length: 100}, (_, index) => ({
    id: index + 1,
    roomNumber: 5200 - index,
  }));
  const calls: number[] = [];
  const room = create(
    () => new RoomSelectComponent(),
    (...args: unknown[]) => {
      const offset = args[1] as number;
      calls.push(offset);
      return of(offset === 0 ? firstPage : [{id: 101, roomNumber: 5000}]);
    },
  );
  room.writeValue(5000);
  deepStrictEqual(room.validate(new FormControl(5000)), {
    roomsUnavailable: true,
  });
  room.ngOnInit();
  deepStrictEqual(calls, [0, 100]);
  equal(room.rooms.length, 101);
  equal(room.selection.value, 5000);
  equal(room.options[0].value, 5000);
  equal(room.validate(new FormControl(5000)), null);
  deepStrictEqual(room.validate(new FormControl(9999)), {roomNotFound: true});
  room.valueField = "id";
  room.ngOnChanges();
  equal(room.options[0].value, 101);
  equal(room.options[0].label, "5000");
  equal(room.validate(new FormControl(101)), null);
});

test("room adapter never offers incomplete rooms or permits a failed load", () => {
  const room = create(
    () => new RoomSelectComponent(),
    () => of([{id: 1}, {roomNumber: 5110}]),
  );
  room.ngOnInit();
  deepStrictEqual(room.options, []);
  equal(room.validate(new FormControl(null)), null);
  const failed = create(
    () => new RoomSelectComponent(),
    () => throwError(() => new Error("Network error")),
  );
  failed.ngOnInit();
  equal(failed.loadFailed, true);
  equal(failed.selection.disabled, true);
  deepStrictEqual(failed.validate(new FormControl(null)), {
    roomsUnavailable: true,
  });
});

test("room adapter propagates an unknown typed query to an optional parent form", () => {
  const room = create(
    () => new RoomSelectComponent(),
    () => of([{id: 42, roomNumber: 5110}]),
  );
  room.ngOnInit();
  const combo = create(() => new ComboboxComponent());
  combo.options = room.options;
  combo.ngOnChanges();
  room.selection.addValidators((control) => combo.validate(control));
  const parent = new FormControl<number | null>(null, (control) =>
    room.validate(control),
  );
  room.registerOnChange((value) => parent.setValue(value));
  room.registerOnValidatorChange(() => parent.updateValueAndValidity());
  combo.registerOnChange((value) => {
    if (typeof value !== "string") room.selection.setValue(value);
  });
  combo.registerOnValidatorChange(() =>
    room.selection.updateValueAndValidity(),
  );
  combo.search("9999");
  equal(parent.invalid, true);
  equal(parent.value, null);
  combo.search("5110");
  equal(parent.valid, true);
  equal(parent.value, 5110);
  combo.search("");
  equal(parent.valid, true);
  equal(parent.value, null);
});
