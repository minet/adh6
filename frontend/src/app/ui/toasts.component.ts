import {ChangeDetectionStrategy, Component, inject} from "@angular/core";
import {NotificationService, ToastKind} from "../notification.service";

// Literal class names so PurgeCSS keeps them
const KIND_CLASS: Record<ToastKind, string> = {
  success: "is-success",
  danger: "is-danger",
  warning: "is-warning",
  info: "is-info",
};

@Component({
  selector: "app-toasts",
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="toasts" aria-live="polite">
      @for (toast of notifications.toasts(); track toast.id) {
        <div class="notification" [class]="kindClass[toast.kind]">
          <button
            type="button"
            class="delete"
            aria-label="Fermer"
            i18n-aria-label="@@common.close"
            (click)="notifications.dismiss(toast.id)"></button>
          <strong>{{ toast.title }}</strong>
          @if (toast.text) {
            <p>{{ toast.text }}</p>
          }
        </div>
      }
    </div>
  `,
  styles: `
    .toasts {
      position: fixed;
      right: 1rem;
      bottom: 1rem;
      z-index: 50;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      max-width: min(24rem, calc(100vw - 2rem));
    }
    .notification {
      margin: 0;
    }
  `,
})
export class ToastsComponent {
  protected readonly notifications = inject(NotificationService);
  protected readonly kindClass = KIND_CLASS;
}
