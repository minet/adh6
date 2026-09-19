import {inject} from "@angular/core";
import {CanActivateFn} from "@angular/router";
import {AuthService} from "./auth.service";

export const authGuard: CanActivateFn = (_route, state) => {
  const auth = inject(AuthService);
  if (auth.isAuthenticated()) return true;
  auth.requireLogin(state.url);
  return false;
};
