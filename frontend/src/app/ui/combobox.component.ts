import {
  Component,
  DestroyRef,
  ElementRef,
  forwardRef,
  inject,
  Input,
  OnChanges,
  EventEmitter,
  Output,
} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {
  AbstractControl,
  ControlValueAccessor,
  FormControl,
  NG_VALIDATORS,
  NG_VALUE_ACCESSOR,
  ValidationErrors,
  Validator,
} from "@angular/forms";

export type ComboboxValue = string | number;

export interface ComboboxOption {
  value: ComboboxValue;
  label: string;
}

let nextComboboxId = 0;

/** Editable suggestions, with strict selection by default and optional free-text search. */
@Component({
  selector: "app-combobox",
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => ComboboxComponent),
      multi: true,
    },
    {
      provide: NG_VALIDATORS,
      useExisting: forwardRef(() => ComboboxComponent),
      multi: true,
    },
  ],
  styles: `
    :host {
      display: block;
      position: relative;
      min-width: 12rem;
    }
    .input {
      padding-right: 2.5rem;
    }
    .combobox-toggle {
      position: absolute;
      top: 0;
      right: 0;
      height: 2.5em;
      width: 2.5rem;
      border: 0;
      background: transparent;
      color: inherit;
      cursor: pointer;
    }
    .combobox-options {
      position: absolute;
      z-index: 20;
      width: 100%;
      max-height: 15rem;
      overflow-y: auto;
      margin: 0;
      padding: 0.25rem 0;
      list-style: none;
      border: 1px solid var(--bulma-border);
      border-radius: 0.375rem;
      background: var(--bulma-scheme-main);
      box-shadow: 0 0.25rem 0.5rem #0002;
    }
    .combobox-options li {
      padding: 0.5rem 0.75rem;
    }
    [role="option"] {
      cursor: pointer;
    }
    [role="option"]:hover,
    [role="option"].active {
      background: var(--bulma-primary);
      color: var(--bulma-primary-invert);
    }
  `,
  template: `
    <div class="control" [class.is-loading]="loading">
      <input
        #searchInput
        class="input is-fullwidth"
        [class.is-danger]="invalidSearch"
        [id]="fieldId"
        type="text"
        role="combobox"
        autocomplete="off"
        [value]="query"
        [placeholder]="placeholder"
        [disabled]="selection.disabled"
        [attr.aria-label]="label"
        [attr.aria-busy]="loading"
        aria-autocomplete="list"
        aria-haspopup="listbox"
        [attr.aria-expanded]="open"
        [attr.aria-controls]="listId"
        [attr.aria-activedescendant]="
          open && activeIndex >= 0 ? listId + '-' + activeIndex : null
        "
        [attr.aria-invalid]="invalidSearch"
        [attr.aria-describedby]="invalidSearch ? fieldId + '-error' : null"
        (input)="search(searchInput.value)"
        (focus)="openOptions()"
        (keydown)="onKeydown($event)"
        (blur)="onBlur()" />
      <button
        type="button"
        class="combobox-toggle"
        tabindex="-1"
        aria-label="Afficher les options"
        i18n-aria-label="@@combobox.show-options"
        [disabled]="selection.disabled"
        (mousedown)="$event.preventDefault()"
        (click)="toggleOptions(searchInput)">
        <span aria-hidden="true">▾</span>
      </button>
    </div>
    @if (open && selection.enabled) {
      <ul
        [id]="listId"
        class="combobox-options"
        role="listbox"
        [attr.aria-label]="label">
        @for (
          option of filteredOptions;
          track option.value;
          let index = $index
        ) {
          <li
            [id]="listId + '-' + index"
            role="option"
            [class.active]="activeIndex === index"
            [attr.aria-selected]="selection.value === option.value"
            (mousedown)="$event.preventDefault()"
            (click)="choose(option)">
            {{ option.label }}
          </li>
        } @empty {
          <li role="presentation" i18n="@@combobox.no-results">
            Aucun résultat
          </li>
        }
      </ul>
    }
    @if (invalidSearch) {
      <p
        [id]="fieldId + '-error'"
        class="help is-danger"
        i18n="@@combobox.invalid-option">
        Sélectionnez une option proposée.
      </p>
    }
    @if (mode === "search" && unavailable) {
      <p class="help is-danger" i18n="@@combobox.suggestions-error">
        Suggestions indisponibles. La recherche reste possible.
      </p>
    }
  `,
})
export class ComboboxComponent
  implements ControlValueAccessor, Validator, OnChanges
{
  @Input() options: readonly ComboboxOption[] = [];
  @Input() label = $localize`:@@combobox.label:Choix`;
  @Input() placeholder =
    $localize`:@@combobox.placeholder:Sélectionner une option`;
  @Input() inputId: string | null = null;
  @Input() loading = false;
  @Input() unavailable = false;
  @Input() mode: "select" | "search" = "select";
  @Input() filterLocally = true;
  @Output() optionSelected = new EventEmitter<ComboboxOption>();
  readonly selection = new FormControl<ComboboxValue | null>(null);
  query = "";
  open = false;
  activeIndex = -1;
  private editing = false;
  private readonly generatedId = `combobox-${nextComboboxId++}`;
  private readonly element = inject<ElementRef<HTMLElement>>(ElementRef, {
    optional: true,
  });
  private disabled = false;
  private onChange: (value: ComboboxValue | null) => void = () => {};
  onTouched: () => void = () => {};
  private onValidatorChange: () => void = () => {};

  get fieldId(): string {
    return this.inputId ?? this.generatedId;
  }

  get listId(): string {
    return `${this.fieldId}-listbox`;
  }

  get filteredOptions(): readonly ComboboxOption[] {
    const query = this.query.trim().toLocaleLowerCase();
    return this.filterLocally && this.editing && query
      ? this.options.filter((option) =>
          option.label.toLocaleLowerCase().includes(query),
        )
      : this.options;
  }

  get invalidSearch(): boolean {
    return (
      this.mode === "select" &&
      this.editing &&
      this.query.trim() !== "" &&
      this.selection.value == null
    );
  }

  constructor() {
    this.selection.valueChanges
      .pipe(takeUntilDestroyed(inject(DestroyRef)))
      .subscribe((value) => {
        this.onChange(value);
      });
  }

  ngOnChanges(): void {
    if (!this.editing && this.mode === "select") {
      this.syncQuery();
    }
    this.activeIndex = this.open && this.filteredOptions.length > 0 ? 0 : -1;
    this.setDisabledState(this.disabled);
    this.onValidatorChange();
  }

  writeValue(value: ComboboxValue | null): void {
    this.selection.setValue(value, {emitEvent: false});
    this.editing = false;
    if (this.mode === "search") {
      this.query = value == null ? "" : String(value);
    } else {
      this.syncQuery();
    }
  }

  registerOnChange(fn: (value: ComboboxValue | null) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(disabled: boolean): void {
    this.disabled = disabled;
    if (
      disabled ||
      (this.mode === "select" && (this.loading || this.unavailable))
    ) {
      this.selection.disable({emitEvent: false});
      this.open = false;
    } else {
      this.selection.enable({emitEvent: false});
    }
  }

  validate(control: AbstractControl): ValidationErrors | null {
    if (this.mode === "search") {
      return null;
    }
    if (this.loading || this.unavailable) {
      return {optionsUnavailable: true};
    }
    if (this.invalidSearch) {
      return {invalidOption: true};
    }
    return control.value == null ||
      this.options.some((option) => option.value === control.value)
      ? null
      : {invalidOption: true};
  }

  registerOnValidatorChange(fn: () => void): void {
    this.onValidatorChange = fn;
  }

  search(query: string): void {
    if (this.selection.disabled) {
      return;
    }
    this.query = query;
    this.editing = true;
    this.open = true;
    this.activeIndex = this.filteredOptions.length > 0 ? 0 : -1;
    const matches = this.options.filter(
      (option) =>
        option.label.toLocaleLowerCase() === query.trim().toLocaleLowerCase(),
    );
    // Typing an exact, unambiguous label is equivalent to selecting its option.
    this.selection.setValue(
      this.mode === "search"
        ? query
        : matches.length === 1
          ? matches[0].value
          : null,
    );
    this.onValidatorChange();
  }

  choose(option: ComboboxOption): void {
    if (
      this.selection.disabled ||
      !this.options.some((item) => item.value === option.value)
    ) {
      return;
    }
    this.editing = false;
    this.query = option.label;
    this.open = false;
    this.selection.setValue(option.value);
    this.onValidatorChange();
    this.optionSelected.emit(option);
  }

  openOptions(): void {
    if (this.selection.disabled) {
      return;
    }
    this.open = true;
    const selectedIndex = this.filteredOptions.findIndex(
      (option) => option.value === this.selection.value,
    );
    this.activeIndex = selectedIndex >= 0 ? selectedIndex : -1;
  }

  toggleOptions(input: Pick<HTMLInputElement, "focus">): void {
    if (this.selection.disabled) {
      return;
    }
    const wasOpen = this.open;
    input.focus();
    if (wasOpen) {
      this.open = false;
    } else {
      this.openOptions();
    }
  }

  onBlur(): void {
    this.open = false;
    if (this.mode === "select" && !this.invalidSearch) {
      this.editing = false;
      this.syncQuery();
    }
    this.onTouched();
  }

  onKeydown(event: Pick<KeyboardEvent, "key" | "preventDefault">): void {
    if (this.selection.disabled) {
      return;
    }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const count = this.filteredOptions.length;
      if (!this.open) {
        this.open = true;
        this.activeIndex =
          count > 0 ? (event.key === "ArrowDown" ? 0 : count - 1) : -1;
      } else if (count > 0) {
        this.activeIndex =
          this.activeIndex < 0
            ? event.key === "ArrowDown"
              ? 0
              : count - 1
            : (this.activeIndex + (event.key === "ArrowDown" ? 1 : count - 1)) %
              count;
      }
      this.element?.nativeElement
        .querySelectorAll<HTMLElement>('[role="option"]')
        [this.activeIndex]?.scrollIntoView({block: "nearest"});
    } else if (event.key === "Enter" && this.open) {
      event.preventDefault();
      const option = this.filteredOptions[this.activeIndex];
      if (option) {
        this.choose(option);
      }
    } else if (event.key === "Escape" && this.open) {
      event.preventDefault();
      this.open = false;
    }
  }

  private syncQuery(): void {
    this.query =
      this.options.find((option) => option.value === this.selection.value)
        ?.label ?? "";
  }
}
