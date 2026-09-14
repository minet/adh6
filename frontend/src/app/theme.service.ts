import {DOCUMENT} from "@angular/common";
import {Injectable, computed, effect, inject, signal} from "@angular/core";

export type ThemeMode = "light" | "dark";

// Also read by the inline script in index.html to avoid a flash on load
const STORAGE_KEY = "adh6-theme";

function initialMode(): ThemeMode {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
  } catch {
    // Storage unavailable: fall back to the OS preference
  }
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

@Injectable({providedIn: "root"})
export class ThemeService {
  private readonly root = inject(DOCUMENT).documentElement;

  readonly mode = signal<ThemeMode>(initialMode());
  readonly isDark = computed(() => this.mode() === "dark");

  constructor() {
    effect(() => this.root.setAttribute("data-theme", this.mode()));
  }

  toggle(): void {
    const mode = this.isDark() ? "light" : "dark";
    this.mode.set(mode);
    try {
      localStorage.setItem(STORAGE_KEY, mode);
    } catch {
      // Storage unavailable: the choice lasts for this tab only
    }
  }
}
