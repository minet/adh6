import {defer, EMPTY, expand, map, Observable, reduce} from "rxjs";
import {AbstractRoom, RoomService, SwitchService} from "../api";
import {ComboboxOption} from "./combobox.component";

/** Load the complete dataset, including an empty final page for exact multiples. */
export function loadAllPages<T>(
  fetchPage: (limit: number, offset: number) => Observable<T[]>,
  pageSize = 100,
): Observable<T[]> {
  return defer(() => fetchPage(pageSize, 0)).pipe(
    expand((page, index) =>
      page.length === pageSize
        ? fetchPage(pageSize, (index + 1) * pageSize)
        : EMPTY,
    ),
    reduce((results, page) => [...results, ...page], [] as T[]),
  );
}

export function loadRooms(service: RoomService): Observable<AbstractRoom[]> {
  return loadAllPages((limit, offset) =>
    service.roomGet(limit, offset, undefined, undefined, [
      "id",
      "roomNumber",
      "description",
    ]),
  ).pipe(
    map((rooms) =>
      rooms
        .filter((room) => room.id != null && room.roomNumber != null)
        .sort((a, b) => a.roomNumber! - b.roomNumber!),
    ),
  );
}

export function loadSwitchOptions(
  service: SwitchService,
): Observable<ComboboxOption[]> {
  return loadAllPages((limit, offset) =>
    service.switchGet(limit, offset, undefined, undefined, [
      "id",
      "description",
      "ip",
    ]),
  ).pipe(
    map((switches) =>
      switches
        .filter((item) => item.id != null)
        .map((item) => ({
          value: item.id!,
          label:
            [item.description, item.ip].filter(Boolean).join(" : ") ||
            `ID ${item.id}`,
        }))
        .sort((a, b) =>
          a.label.localeCompare(b.label, undefined, {numeric: true}),
        ),
    ),
  );
}
