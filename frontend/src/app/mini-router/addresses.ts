import {MiniRouter} from "../api";

export type MiniRouterAddresses = Pick<
  MiniRouter,
  "ipWireguard" | "ipVlan31" | "macAccept" | "macDeny"
>;

export const MIN_NUMBER = 1;
export const MAX_NUMBER = 254;

/** Same derivation as the backend, to preview the addresses while typing. */
export function addressesOf(number: number): MiniRouterAddresses {
  // 115 -> "01:15", 98 -> "00:98"
  const digits = String(number).padStart(3, "0");
  const macSuffix = `0${digits[0]}:${digits.slice(1)}`;
  return {
    ipWireguard: `10.31.0.${number}`,
    ipVlan31: `172.30.0.${number}`,
    macAccept: `00:00:36:00:${macSuffix}`,
    macDeny: `36:36:36:00:${macSuffix}`,
  };
}
