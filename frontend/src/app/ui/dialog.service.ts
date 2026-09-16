import {Injectable, signal} from "@angular/core";

export interface DialogInput {
  type: "text" | "number";
  value: string;
  label?: string;
  placeholder?: string;
  validate?: (value: string) => string | null;
}

export interface DialogRequest {
  title: string;
  text?: string;
  confirmText: string;
  cancelText: string | null;
  danger: boolean;
  input?: DialogInput;
  resolve: (value: string | null) => void;
}

@Injectable({
  providedIn: "root",
})
export class DialogService {
  private readonly _current = signal<DialogRequest | null>(null);
  readonly current = this._current.asReadonly();

  confirm(options: {
    title: string;
    text?: string;
    confirmText?: string;
    danger?: boolean;
  }): Promise<boolean> {
    return this.open({
      title: options.title,
      text: options.text,
      confirmText:
        options.confirmText ?? $localize`:@@common.confirm:Confirmer`,
      cancelText: $localize`:@@common.cancel:Annuler`,
      danger: options.danger ?? false,
    }).then((value) => value !== null);
  }

  prompt(options: {
    title: string;
    text?: string;
    label?: string;
    type?: "text" | "number";
    value?: string;
    placeholder?: string;
    confirmText?: string;
    validate?: (value: string) => string | null;
  }): Promise<string | null> {
    return this.open({
      title: options.title,
      text: options.text,
      confirmText: options.confirmText ?? $localize`:@@validate:Valider`,
      cancelText: $localize`:@@common.cancel:Annuler`,
      danger: false,
      input: {
        type: options.type ?? "text",
        value: options.value ?? "",
        label: options.label,
        placeholder: options.placeholder,
        validate: options.validate,
      },
    });
  }

  alert(options: {title: string; text?: string}): Promise<void> {
    return this.open({
      ...options,
      confirmText: "OK",
      cancelText: null,
      danger: false,
    }).then(() => undefined);
  }

  /** Resolves the open dialog: the input value (or "") on confirm, null on cancel. */
  close(value: string | null): void {
    const request = this._current();
    if (!request) {
      return;
    }
    this._current.set(null);
    request.resolve(value);
  }

  private open(
    request: Omit<DialogRequest, "resolve">,
  ): Promise<string | null> {
    this.close(null);
    return new Promise((resolve) => this._current.set({...request, resolve}));
  }
}
