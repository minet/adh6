import {ChangeDetectionStrategy, Component, input, output} from "@angular/core";

@Component({
  selector: "app-modal",
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {"(document:keydown.escape)": "closed.emit()"},
  styles: `
    .modal-card {
      width: min(40rem, calc(100vw - 2rem));
      max-height: calc(100dvh - 2rem);
      margin: 1rem;
      border: 1px solid var(--app-line);
      border-radius: 0.875rem;
    }
    .modal-card-head,
    .modal-card-foot {
      padding: 1.25rem 1.5rem;
      background: var(--bulma-scheme-main);
      box-shadow: none;
    }
    .modal-card-head {
      border-bottom: 1px solid var(--app-line);
    }
    .modal-card-title {
      font-size: 1.25rem;
      font-weight: 600;
    }
    .modal-card-body {
      padding: 1.5rem;
      overscroll-behavior: contain;
    }
    .modal-card-foot {
      border-top: 1px solid var(--app-line);
    }
    @media (max-width: 480px) {
      .modal-card-head,
      .modal-card-body,
      .modal-card-foot {
        padding: 1rem;
      }
    }
  `,
  template: `
    <div class="modal is-active">
      <div class="modal-background" (click)="closed.emit()"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">{{ title() }}</p>
          <button
            type="button"
            class="delete"
            aria-label="Fermer"
            i18n-aria-label="@@common.close"
            (click)="closed.emit()"></button>
        </header>
        <section class="modal-card-body">
          <ng-content />
        </section>
        <footer class="modal-card-foot">
          <ng-content select="[modal-actions]" />
        </footer>
      </div>
    </div>
  `,
})
export class ModalComponent {
  readonly title = input.required<string>();
  readonly closed = output<void>();
}
