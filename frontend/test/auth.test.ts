import "./fake-window";
import "@angular/compiler";
import "@angular/localize/init";
import {DOCUMENT} from "@angular/common";
import {
  HttpClient,
  HttpErrorResponse,
  HttpEvent,
  HttpRequest,
  HttpResponse,
} from "@angular/common/http";
import {Injector, runInInjectionContext} from "@angular/core";
import {ActivatedRouteSnapshot, RouterStateSnapshot} from "@angular/router";
import {deepStrictEqual, equal, ok} from "node:assert/strict";
import {test} from "node:test";
import {Observable, Subject, of, throwError} from "rxjs";
import {Member, MiscService} from "../src/app/api";
import {AppAbility, abilityRulesFor} from "../src/app/auth/ability";
import {authGuard} from "../src/app/auth/auth.guard";
import {authInterceptor} from "../src/app/auth/auth.interceptor";
import {AuthService} from "../src/app/auth/auth.service";
import {DialogService} from "../src/app/ui/dialog.service";

const API = "https://adh6.test/api";

function httpError(status: number): HttpErrorResponse {
  return new HttpErrorResponse({status});
}

function interceptorSetup(refresh: () => Observable<void>) {
  const events = {expired: 0, refreshed: 0};
  const injector = Injector.create({
    providers: [
      {
        provide: AuthService,
        useValue: {
          refreshSession: () => {
            events.refreshed++;
            return refresh();
          },
          expireSession: () => events.expired++,
        },
      },
    ],
  });
  const sent: HttpRequest<unknown>[] = [];
  const run = (
    url: string,
    respond: (attempt: number) => Observable<HttpEvent<unknown>>,
  ) => {
    let attempt = 0;
    const next = (req: HttpRequest<unknown>) => {
      sent.push(req);
      return respond(attempt++);
    };
    return runInInjectionContext(injector, () =>
      authInterceptor(new HttpRequest("GET", url), next),
    );
  };
  return {events, sent, run};
}

const ok200 = () => of(new HttpResponse({status: 200}));

test("a missing role never grants a right", () => {
  deepStrictEqual(abilityRulesFor({}), []);
  deepStrictEqual(abilityRulesFor({roles: ["admin:read"]}), []);
});

test("rights follow the roles and the member of the profile", () => {
  const rules = abilityRulesFor({
    roles: ["admin:read", "admin:write", "network:read"],
    member: {id: 12} as Member,
  });
  deepStrictEqual(
    rules.map((rule) => [rule.action, rule.subject]),
    [
      ["manage", "admin"],
      ["read", "network"],
      ["read", "Member"],
    ],
  );
});

test("API calls say they come from the app and carry no token of their own", async () => {
  const {sent, run} = interceptorSetup(() => of(undefined));
  await new Promise((resolve) =>
    run(`${API}/member`, ok200).subscribe({complete: () => resolve(null)}),
  );
  equal(sent[0].headers.get("X-Requested-With"), "XMLHttpRequest");
  equal(sent[0].headers.has("Authorization"), false);
});

test("requests to other servers are left alone", async () => {
  const {sent, run} = interceptorSetup(() => of(undefined));
  await new Promise((resolve) =>
    run("https://keycloak.test/token", ok200).subscribe({
      complete: () => resolve(null),
    }),
  );
  equal(sent[0].headers.has("X-Requested-With"), false);
});

test("the session routes are never retried", async () => {
  const {events, sent, run} = interceptorSetup(() => of(undefined));
  const error = await new Promise<HttpErrorResponse>((resolve) =>
    run(`${API}/auth/refresh`, () =>
      throwError(() => httpError(401)),
    ).subscribe({error: resolve}),
  );
  equal(error.status, 401);
  equal(sent.length, 1);
  equal(sent[0].headers.get("X-Requested-With"), "XMLHttpRequest");
  deepStrictEqual(events, {expired: 0, refreshed: 0});
});

test("a 401 renews the session once and retries the call", async () => {
  const {events, sent, run} = interceptorSetup(() => of(undefined));
  const status = await new Promise<number>((resolve) =>
    run(`${API}/member`, (attempt) =>
      attempt === 0 ? throwError(() => httpError(401)) : ok200(),
    ).subscribe((event) => resolve((event as HttpResponse<unknown>).status)),
  );
  equal(status, 200);
  equal(sent.length, 2);
  deepStrictEqual(events, {expired: 0, refreshed: 1});
});

test("a session Keycloak refuses to renew ends and reports the original 401", async () => {
  const {events, sent, run} = interceptorSetup(() =>
    throwError(() => httpError(401)),
  );
  const error = await new Promise<HttpErrorResponse>((resolve) =>
    run(`${API}/member`, () => throwError(() => httpError(401))).subscribe({
      error: resolve,
    }),
  );
  equal(error.status, 401);
  equal(sent.length, 1);
  deepStrictEqual(events, {expired: 1, refreshed: 1});
});

test("a login service that is down does not end the session", async () => {
  const {events, run} = interceptorSetup(() =>
    throwError(() => httpError(503)),
  );
  const error = await new Promise<HttpErrorResponse>((resolve) =>
    run(`${API}/member`, () => throwError(() => httpError(401))).subscribe({
      error: resolve,
    }),
  );
  equal(error.status, 401);
  deepStrictEqual(events, {expired: 0, refreshed: 1});
});

test("a 401 that survives the renewal ends the session", async () => {
  const {events, run} = interceptorSetup(() => of(undefined));
  await new Promise((resolve) =>
    run(`${API}/member`, () => throwError(() => httpError(401))).subscribe({
      error: resolve,
    }),
  );
  deepStrictEqual(events, {expired: 1, refreshed: 1});
});

test("other failures neither renew nor end the session", async () => {
  const {events, run} = interceptorSetup(() => of(undefined));
  const error = await new Promise<HttpErrorResponse>((resolve) =>
    run(`${API}/member`, () => throwError(() => httpError(500))).subscribe({
      error: resolve,
    }),
  );
  equal(error.status, 500);
  deepStrictEqual(events, {expired: 0, refreshed: 0});
});

function guardSetup(isAuthenticated: boolean) {
  const logins: string[] = [];
  const injector = Injector.create({
    providers: [
      {
        provide: AuthService,
        useValue: {
          isAuthenticated: () => isAuthenticated,
          requireLogin: (url: string) => logins.push(url),
        },
      },
    ],
  });
  const state = {url: "/member/12?tab=devices"} as RouterStateSnapshot;
  return {
    logins,
    run: () =>
      runInInjectionContext(injector, () =>
        authGuard({} as ActivatedRouteSnapshot, state),
      ),
  };
}

test("an anonymous visitor is sent to sign in and brought back to the requested page", () => {
  const {logins, run} = guardSetup(false);
  equal(run(), false);
  deepStrictEqual(logins, ["/member/12?tab=devices"]);
});

test("a signed-in user passes the guard", () => {
  const {logins, run} = guardSetup(true);
  equal(run(), true);
  deepStrictEqual(logins, []);
});

function serviceSetup(
  options: {
    url?: string;
    profile?: () => Observable<unknown>;
    retry?: boolean;
    keepStorage?: boolean;
  } = {},
) {
  if (!options.keepStorage) sessionStorage.clear();
  const url = new URL(options.url ?? "https://adh6.test/en/switch/3");
  const assigned: string[] = [];
  const replaced: string[] = [];
  const posts: string[] = [];
  const reloads: string[] = [];
  const dialogs: {text?: string}[] = [];
  const document = {
    baseURI: "https://adh6.test/en/",
    location: {
      href: url.href,
      pathname: url.pathname,
      search: url.search,
      assign: (target: string) => assigned.push(target),
      reload: () => reloads.push("reload"),
    },
    defaultView: {
      history: {
        replaceState: (_state: unknown, _title: string, target: URL) => {
          replaced.push(target.pathname + target.search);
          document.location.pathname = target.pathname;
          document.location.search = target.search;
        },
      },
    },
  };
  const ability = new AppAbility();
  const injector = Injector.create({
    providers: [
      {provide: DOCUMENT, useValue: document},
      {
        provide: HttpClient,
        useValue: {
          post: (target: string) => {
            posts.push(target);
            return of({logout_url: "https://keycloak.test/logout"});
          },
        },
      },
      {provide: AppAbility, useValue: ability},
      {
        provide: MiscService,
        useValue: {
          profile:
            options.profile ??
            (() => of({roles: ["admin:read", "admin:write"]})),
        },
      },
      {
        provide: DialogService,
        useValue: {
          confirm: (dialog: {text?: string}) => {
            dialogs.push(dialog);
            return Promise.resolve(options.retry ?? false);
          },
        },
      },
      AuthService,
    ],
  });
  const settled = () => new Promise((resolve) => setTimeout(resolve));
  return {
    service: injector.get(AuthService),
    ability,
    assigned,
    replaced,
    posts,
    reloads,
    dialogs,
    settled,
  };
}

const loginUrl = (path: string) =>
  `${API}/auth/login?return_to=${encodeURIComponent(path)}`;

test("an anonymous visitor goes to Keycloak and comes back to the page they asked for", () => {
  const {service, assigned} = serviceSetup();
  service.requireLogin("/member/12?tab=devices");
  deepStrictEqual(assigned, [loginUrl("/en/member/12?tab=devices")]);
});

test("the guard and the interceptor asking together send the user only once", () => {
  const {service, assigned} = serviceSetup();
  service.requireLogin("/member/12");
  service.expireSession();
  service.requireLogin("/member/12");
  equal(assigned.length, 1);
});

test("a signed-in user gets their rights", async () => {
  const {service, ability} = serviceSetup();
  await service.initialize();
  equal(service.isAuthenticated(), true);
  ok(ability.can("manage", "admin"));
});

test("a visitor who is not signed in gets no rights and no dialog", async () => {
  const {service, ability, dialogs} = serviceSetup({
    profile: () => throwError(() => httpError(401)),
  });
  await service.initialize();
  equal(service.isAuthenticated(), false);
  ok(!ability.can("manage", "admin"));
  equal(dialogs.length, 0);
});

test("a server outage is not mistaken for a visitor who is not signed in", async () => {
  const {service, assigned, reloads, dialogs, settled} = serviceSetup({
    profile: () => throwError(() => httpError(503)),
    retry: true,
  });
  await service.initialize();
  await settled();

  equal(dialogs.length, 1);
  ok(dialogs[0].text?.includes("serveur"));
  // Signing in again cannot fix an outage: the guard must not start a login...
  service.requireLogin("/member/12");
  equal(assigned.length, 0);
  // ...and retrying just reloads the page.
  equal(reloads.length, 1);
});

test("a login the backend refused is explained and not started again by itself", async () => {
  const {service, assigned, replaced, dialogs, settled} = serviceSetup({
    url: "https://adh6.test/en/member/12?tab=devices&auth_error=login_failed",
  });
  await service.initialize();
  await settled();
  equal(dialogs.length, 1);
  deepStrictEqual(replaced, ["/en/member/12?tab=devices"]);
  equal(service.isAuthenticated(), false);

  service.requireLogin("/member/12");
  equal(assigned.length, 0);
});

test("an unavailable login service is reported as such", async () => {
  const {service, dialogs, settled} = serviceSetup({
    url: "https://adh6.test/en/?auth_error=provider_unavailable",
  });
  await service.initialize();
  await settled();
  ok(dialogs[0].text?.includes("indisponible"));
});

test("retrying after a failure signs in again on the current page", async () => {
  const {service, assigned, settled} = serviceSetup({
    url: "https://adh6.test/en/member/12?auth_error=login_failed",
    retry: true,
  });
  await service.initialize();
  await settled();
  deepStrictEqual(assigned, [loginUrl("/en/member/12")]);
});

test("a lost session signs the user in again on the current page", () => {
  const {service, assigned} = serviceSetup();
  service.expireSession();
  deepStrictEqual(assigned, [loginUrl("/en/switch/3")]);
});

test("a login that is immediately rejected by the API stops instead of looping", async () => {
  serviceSetup().service.requireLogin("/switch/3");

  // Back from Keycloak in a new page load, and the API still refuses the session.
  const back = serviceSetup({keepStorage: true});
  back.service.expireSession();
  await back.settled();

  equal(back.assigned.length, 0);
  equal(back.dialogs.length, 1);
  ok(back.dialogs[0].text?.includes("refusé"));
});

test("logging out closes the session here, then in Keycloak", () => {
  const {service, ability, posts, assigned} = serviceSetup();
  ability.update([{action: "manage", subject: "admin"}]);

  service.logout();

  deepStrictEqual(posts, [`${API}/auth/logout`]);
  deepStrictEqual(assigned, ["https://keycloak.test/logout"]);
  ok(!ability.can("manage", "admin"));
  equal(service.isAuthenticated(), false);
});

test("concurrent renewals share one request", () => {
  const renewals = new Subject<void>();
  const {service, posts} = serviceSetup();
  const http = (service as unknown as {http: {post: (url: string) => unknown}})
    .http;
  http.post = (url: string) => {
    posts.push(url);
    return renewals;
  };

  service.refreshSession().subscribe();
  service.refreshSession().subscribe();
  renewals.next();
  renewals.complete();

  deepStrictEqual(posts, [`${API}/auth/refresh`]);
});
