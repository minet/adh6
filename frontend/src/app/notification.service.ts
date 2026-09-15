import {Injectable, signal} from "@angular/core";

export type ToastKind = "success" | "danger" | "warning" | "info";

export interface Toast {
  id: number;
  kind: ToastKind;
  title: string;
  text?: string;
}

const ERROR_TITLES: Record<number, string> = {
  400: "Bad Request",
  401: "Unauthenticated",
  403: "Unauthorize",
  404: "Not Found",
  500: "Internal server Error",
};

@Injectable({
  providedIn: "root",
})
export class NotificationService {
  private nextId = 0;
  private readonly _toasts = signal<Toast[]>([]);
  readonly toasts = this._toasts.asReadonly();

  show(kind: ToastKind, title: string, text?: string, timer = 3000): void {
    const id = this.nextId++;
    this._toasts.update((toasts) => [...toasts, {id, kind, title, text}]);
    setTimeout(() => this.dismiss(id), timer);
  }

  dismiss(id: number): void {
    this._toasts.update((toasts) => toasts.filter((t) => t.id !== id));
  }

  errorNotification(
    errorCode: number,
    title?: string,
    message?: string,
    timer?: number,
  ): void {
    const base = ERROR_TITLES[errorCode] ?? "Error";
    this.show("danger", base + (title ? " - " + title : ""), message, timer);
  }

  successNotification(
    title = $localize`:@@notification.success:Opération réussie`,
    message?: string,
    timer?: number,
  ): void {
    this.show("success", title, message, timer);
  }
}
