import {
  Ability,
  AbilityBuilder,
  AbilityClass,
  PureAbility,
} from "@casl/ability";
import {Provider} from "@angular/core";
import {Profile200Response} from "../api";

type Actions = "manage" | "read" | "free";
type Subjects = string;

export type AppAbility = Ability<[Actions, Subjects]>;
export const AppAbility = Ability as AbilityClass<AppAbility>;

export function provideAbility(): Provider[] {
  return [
    {provide: AppAbility, useValue: new AppAbility()},
    {provide: PureAbility, useExisting: AppAbility},
  ];
}

export function abilityRulesFor(profile: Profile200Response) {
  const roles = new Set(profile.roles ?? []);
  const hasAll = (...required: string[]) =>
    required.every((role) => roles.has(role));

  const {can, rules} = new AbilityBuilder<AppAbility>(AppAbility);
  if (hasAll("admin:read", "admin:write")) can("manage", "admin");
  if (hasAll("admin:prod", "admin:write")) can("manage", "prod");
  if (hasAll("network:read")) can("read", "network");
  if (hasAll("network:read", "network:write")) can("manage", "network");
  if (hasAll("treasurer:write")) can("free", "Membership");
  if (hasAll("treasurer:read", "treasurer:write")) can("manage", "treasury");
  if (profile.member?.id != null) {
    can("read", "Member", {id: profile.member.id});
  }
  return rules;
}
