import {AbstractPort, DiscoveredPort} from "../api";

export function portOidKey(oid: string | undefined): string | null {
  const value = (oid ?? "").trim();
  return /^[0-9]{1,10}$/.test(value) &&
    Number(value) > 0 &&
    Number(value) <= 2147483647
    ? String(Number(value))
    : null;
}

export function missingDiscoveredPorts(
  existing: readonly AbstractPort[],
  discovered: readonly DiscoveredPort[],
): DiscoveredPort[] {
  const seen = new Set(existing.map((port) => portOidKey(port.oid)));
  return discovered
    .filter((port) => {
      const oid = portOidKey(port.oid);
      if (!oid || !port.portNumber?.trim() || seen.has(oid)) return false;
      seen.add(oid);
      return true;
    })
    .map((port) => ({...port, oid: portOidKey(port.oid)!}));
}
