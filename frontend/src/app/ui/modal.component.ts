import {ChangeDetectionStrategy, Component, input, output} from "@angular/core";

@Component({
  selector: "app-modal",
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {"(document:keydown.escape)": "closed.emit()"},
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
