import {Route} from "@angular/router";

export const ROUTES: Route[] = [
  {path: "", redirectTo: "search", pathMatch: "full"},
  {
    path: "search",
    loadComponent: () =>
      import("./mini-router-list.component").then(
        (c) => c.MiniRouterListComponent,
      ),
  },
  {
    path: "add",
    loadComponent: () =>
      import("./mini-router-new.component").then(
        (c) => c.MiniRouterNewComponent,
      ),
  },
  {
    path: "view/:id",
    loadComponent: () =>
      import("./mini-router-details.component").then(
        (c) => c.MiniRouterDetailsComponent,
      ),
  },
];
