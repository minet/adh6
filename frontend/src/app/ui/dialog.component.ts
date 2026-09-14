import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  effect,
  inject,
  signal,
  viewChild,
} from "@angular/core";
import {DialogRequest, DialogService} from "./dialog.service";
import {ModalComponent} from "./modal.component";

@Component({
  selector: "app-dialog",
  imports: [ModalComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (dialog.current(); as request) {
      <app-modal [title]="request.title" (closed)="dialog.close(null)">
        @if (request.text) {
          <p class="dialog-text">{{ request.text }}</p>
        }
        <form id="app-dialog-form" (submit)="submit($event, request)">
          @if (request.input; as field) {
            <div class="field mt-3">
              @if (field.label) {
                <label class="label" for="app-dialog-input">{{
                  field.label
                }}</label>
              }
              <input
                #field
                id="app-dialog-input"
                class="input"
                [class.is-danger]="error()"
                [type]="field.type"
                [value]="value()"
                [placeholder]="field.placeholder ?? ''"
                (input)="onInput($event)" />
              @if (error(); as message) {
                <p class="help is-danger">{{ message }}</p>
              }
            </div>
          }
        </form>
        <div modal-actions class="buttons">
          <button
            type="submit"
            form="app-dialog-form"
            class="button"
            [class.is-danger]="request.danger"
            [class.is-primary]="!request.danger">
            {{ request.confirmText }}
          </button>
          @if (request.cancelText) {
            <button type="button" class="button" (click)="dialog.close(null)">
              {{ request.cancelText }}
            </button>
          }
        </div>
      </app-modal>
    }
  `,
  styles: `
    .dialog-text {
      white-space: pre-line;
    }
  `,
})
export class DialogComponent {
  protected readonly dialog = inject(DialogService);
  protected readonly value = signal("");
  protected readonly error = signal<string | null>(null);
  private readonly field = viewChild<ElementRef<HTMLInputElement>>("field");

  constructor() {
    effect(() => {
      this.value.set(this.dialog.current()?.input?.value ?? "");
      this.error.set(null);
    });
    effect(() => this.field()?.nativeElement.focus());
  }

  protected onInput(event: Event): void {
    this.value.set((event.target as HTMLInputElement).value);
    this.error.set(null);
  }

  protected submit(event: Event, request: DialogRequest): void {
    event.preventDefault();
    const value = this.value().trim();
    const error = request.input?.validate?.(value) ?? null;
    if (error) {
      this.error.set(error);
      return;
    }
    this.dialog.close(value);
  }
}
