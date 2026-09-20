// environment.ts reads `window.location` when it is imported.
const storage = new Map<string, string>();

Object.assign(globalThis, {
  window: {location: {host: "adh6.test", origin: "https://adh6.test"}},
  sessionStorage: {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => void storage.set(key, value),
    removeItem: (key: string) => void storage.delete(key),
    clear: () => storage.clear(),
  },
});
