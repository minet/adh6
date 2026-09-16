import {
  parseTemplate,
  TmplAstElement,
  TmplAstIfBlock,
  TmplAstNode,
  TmplAstText,
} from "@angular/compiler";
import {deepStrictEqual, equal, ok} from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {inject, Injector, runInInjectionContext} from "@angular/core";
import {HttpErrorResponse} from "@angular/common/http";
import {UntypedFormBuilder} from "@angular/forms";
import {ActivatedRoute, Router} from "@angular/router";
import {Observable, of, Subject, throwError} from "rxjs";
import {
  MemberService,
  PortService,
  RoomMembersService,
  RoomService,
  SwitchService,
} from "../src/app/api";
import {RoomDetailsComponent} from "../src/app/room/room-details/room-details.component";
import {NotificationService} from "../src/app/notification.service";
import {DialogService} from "../src/app/ui/dialog.service";

function setup(
  confirm: () => Promise<boolean> = () => Promise.resolve(true),
  response: () => Observable<unknown> = () => of(null),
) {
  const deletedIds: number[] = [];
  const portChanges: {id: number; body: unknown}[] = [];
  const navigations: unknown[][] = [];
  const successes: unknown[][] = [];
  const errors: unknown[][] = [];
  let confirmations = 0;
  const injector = Injector.create({
    providers: [
      {
        provide: DialogService,
        useValue: {
          confirm: () => {
            confirmations++;
            return confirm();
          },
        },
      },
      {
        provide: NotificationService,
        useValue: {
          successNotification: (...args: unknown[]) => successes.push(args),
          errorNotification: (...args: unknown[]) => errors.push(args),
        },
      },
      {
        provide: Router,
        useValue: {
          navigate: (commands: unknown[]) => {
            navigations.push(commands);
            return Promise.resolve(true);
          },
        },
      },
      {provide: ActivatedRoute, useValue: {params: of({room_id: "42"})}},
      {
        provide: RoomService,
        useValue: {
          roomIdGet: () => of({id: 42, roomNumber: 5110}),
          roomIdDelete: (id: number) => {
            deletedIds.push(id);
            return response();
          },
        },
      },
      {provide: RoomMembersService, useValue: {}},
      {provide: MemberService, useValue: {}},
      {
        provide: PortService,
        useValue: {
          portGet: () => of([]),
          portIdRoomPatch: (id: number, body: unknown) => {
            portChanges.push({id, body});
            return response();
          },
        },
      },
      {provide: SwitchService, useValue: {}},
      {provide: UntypedFormBuilder, useValue: new UntypedFormBuilder()},
    ],
  });
  const component = runInInjectionContext(
    injector,
    () =>
      new RoomDetailsComponent(
        inject(NotificationService),
        inject(Router),
        inject(RoomMembersService),
        inject(RoomService),
        inject(PortService),
        inject(MemberService),
        inject(SwitchService),
        inject(UntypedFormBuilder),
        inject(ActivatedRoute),
      ),
  );
  return {
    component,
    deletedIds,
    portChanges,
    navigations,
    successes,
    errors,
    destroy: () => injector.destroy(),
    confirmations: () => confirmations,
  };
}

test("confirmed room deletion uses the database ID and returns to the room list", async () => {
  const state = setup();
  await state.component.deleteRoom({id: 42, roomNumber: 5110});
  equal(state.confirmations(), 1);
  equal(state.component.deleting, false);
  equal(state.deletedIds[0], 42);
  equal(state.navigations[0].join("/"), "/room/search");
  equal(state.successes.length, 1);
  equal(state.errors.length, 0);
});

test("cancelling room deletion does not call the API or navigate", async () => {
  const state = setup(() => Promise.resolve(false));
  await state.component.deleteRoom({id: 42, roomNumber: 5110});
  equal(state.deletedIds.length, 0);
  equal(state.navigations.length, 0);
  equal(state.successes.length, 0);
  equal(state.component.deleting, false);
});

test("room deletion reports API failures and re-enables the button for a retry", async () => {
  const state = setup(undefined, () =>
    throwError(() => new HttpErrorResponse({status: 403})),
  );
  await state.component.deleteRoom({id: 42, roomNumber: 5110});
  equal(state.navigations.length, 0);
  equal(state.successes.length, 0);
  equal(state.errors[0][0], 403);
  equal(state.component.deleting, false);
});

test("room deletion blocks duplicate clicks while confirmation or the request is pending", async () => {
  let resolveConfirmation!: (confirmed: boolean) => void;
  const confirmation = new Promise<boolean>((resolve) => {
    resolveConfirmation = resolve;
  });
  const response = new Subject<unknown>();
  const state = setup(
    () => confirmation,
    () => response,
  );
  const first = state.component.deleteRoom({id: 42, roomNumber: 5110});
  await state.component.deleteRoom({id: 42, roomNumber: 5110});
  equal(state.confirmations(), 1);
  equal(state.component.deleting, true);
  resolveConfirmation(true);
  await Promise.resolve();
  await state.component.deleteRoom({id: 42, roomNumber: 5110});
  equal(state.deletedIds.length, 1);
  response.next(null);
  await first;
  equal(state.component.deleting, false);
});

test("room deletion is not started for an invalid ID or after leaving the page", async () => {
  const state = setup();
  await state.component.deleteRoom({roomNumber: 5110});
  equal(state.confirmations(), 0);
  state.destroy();
  await state.component.deleteRoom({id: 42, roomNumber: 5110});
  equal(state.deletedIds.length, 0);
});

test("room deletion button is not permanently disabled and has a click handler", () => {
  const template = readFileSync(
    "src/app/room/room-details/room-details.component.html",
    "utf8",
  );
  const parsed = parseTemplate(template, "room-details.component.html");
  equal(parsed.errors, null);
  function findDeleteButton(nodes: TmplAstNode[]): TmplAstElement | undefined {
    for (const node of nodes) {
      if (
        node instanceof TmplAstElement &&
        node.name === "button" &&
        node.children.some(
          (child) =>
            child instanceof TmplAstText && child.value.trim() === "Supprimer",
        )
      ) {
        return node;
      }
      if (node instanceof TmplAstElement) {
        const button = findDeleteButton(node.children);
        if (button) return button;
      }
      if (node instanceof TmplAstIfBlock) {
        for (const branch of node.branches) {
          const button = findDeleteButton(branch.children);
          if (button) return button;
        }
      }
    }
    return undefined;
  }
  const button = findDeleteButton(parsed.nodes);
  ok(button, "The room deletion button must exist");
  equal(
    button.attributes.some((attribute) => attribute.name === "disabled"),
    false,
  );
  ok(
    button.outputs.some((output) => output.name === "click"),
    "Deletion must be wired to a click handler",
  );
});

test("port removal clears only the room assignment and refreshes the list", async () => {
  const state = setup();
  await state.component.detachPort({
    id: 7,
    room: 42,
    switchObj: 1,
    oid: "10101",
    portNumber: "Gi1/0/1",
  });
  deepStrictEqual(state.portChanges, [
    {id: 7, body: {room: null, expectedRoom: 42}},
  ]);
  equal(state.deletedIds.length, 0);
  equal(state.successes.length, 1);
  equal(state.component.detachingPortIds.size, 0);
  state.destroy();
});

test("cancelled port removal keeps the assignment", async () => {
  const state = setup(() => Promise.resolve(false));
  await state.component.detachPort({id: 7, room: 42});
  equal(state.portChanges.length, 0);
  equal(state.successes.length, 0);
  state.destroy();
});

test("failed port removal reports the error and allows retry", async () => {
  const state = setup(
    () => Promise.resolve(true),
    () => throwError(() => new HttpErrorResponse({status: 409})),
  );
  await state.component.detachPort({id: 7, room: 42});
  equal(state.errors[0][0], 409);
  equal(state.successes.length, 0);
  equal(state.component.detachingPortIds.size, 0);
  state.destroy();
});

test("port removal cannot be submitted twice while confirmation is pending", async () => {
  let confirm!: (value: boolean) => void;
  const state = setup(
    () =>
      new Promise((resolve) => {
        confirm = resolve;
      }),
  );
  const first = state.component.detachPort({id: 7, room: 42});
  await state.component.detachPort({id: 7, room: 42});
  equal(state.confirmations(), 1);
  confirm(true);
  await first;
  equal(state.portChanges.length, 1);
  state.destroy();
});

test("port removal is cancelled if the user switches rooms while confirming", async () => {
  let confirm!: (value: boolean) => void;
  const state = setup(
    () =>
      new Promise((resolve) => {
        confirm = resolve;
      }),
  );
  const pending = state.component.detachPort({id: 7, room: 42});
  state.component.room_id = 43;
  confirm(true);
  await pending;
  equal(state.portChanges.length, 0);
  state.destroy();
});
