import {
  Component,
  DestroyRef,
  forwardRef,
  inject,
  Input,
  OnChanges,
  OnInit,
} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {
  AbstractControl,
  ControlValueAccessor,
  FormControl,
  NG_VALIDATORS,
  NG_VALUE_ACCESSOR,
  ReactiveFormsModule,
  ValidationErrors,
  Validator,
} from "@angular/forms";
import {AbstractRoom, RoomService} from "../api";
import {ComboboxComponent, ComboboxOption} from "./combobox.component";
import {loadRooms} from "./entity-options";

@Component({
  selector: "app-room-select",
  imports: [ReactiveFormsModule, ComboboxComponent],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => RoomSelectComponent),
      multi: true,
    },
    {
      provide: NG_VALIDATORS,
      useExisting: forwardRef(() => RoomSelectComponent),
      multi: true,
    },
  ],
  template: `
    <app-combobox
      [formControl]="selection"
      [options]="options"
      [loading]="loading"
      [unavailable]="loadFailed"
      label="Numéro de chambre"
      i18n-label="@@room.select.label"
      [placeholder]="placeholder"
      (focusout)="onTouched()" />
    @if (loadFailed) {
      <p class="help is-danger" i18n="@@room.select.load-error">
        Impossible de charger les chambres.
      </p>
    } @else if (!loading && rooms.length === 0) {
      <p class="help" i18n="@@room.select.empty">Aucune chambre disponible.</p>
    }
  `,
})
export class RoomSelectComponent
  implements ControlValueAccessor, Validator, OnInit, OnChanges
{
  @Input() valueField: "id" | "roomNumber" = "roomNumber";
  @Input() placeholder =
    $localize`:@@room.select.placeholder:Sélectionner une chambre`;
  readonly selection = new FormControl<number | null>({
    value: null,
    disabled: true,
  });
  rooms: AbstractRoom[] = [];
  options: ComboboxOption[] = [];
  loading = true;
  loadFailed = false;
  private disabled = false;
  private readonly roomService = inject(RoomService);
  private readonly destroyRef = inject(DestroyRef);
  private onChange: (value: number | null) => void = () => {};
  onTouched: () => void = () => {};
  private onValidatorChange: () => void = () => {};

  ngOnChanges(): void {
    this.options = this.rooms.map((room) => ({
      value: room[this.valueField]!,
      label: String(room.roomNumber),
    }));
    this.onValidatorChange();
  }

  ngOnInit(): void {
    this.selection.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((value) => {
        this.onChange(value);
      });
    this.selection.statusChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.onValidatorChange());

    loadRooms(this.roomService)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (rooms) => {
          this.rooms = rooms;
          this.loading = false;
          this.ngOnChanges();
          this.setDisabledState(this.disabled);
        },
        error: () => {
          this.loading = false;
          this.loadFailed = true;
          this.onValidatorChange();
        },
      });
  }

  writeValue(value: number | null): void {
    this.selection.setValue(value, {emitEvent: false});
  }

  registerOnChange(fn: (value: number | null) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(disabled: boolean): void {
    this.disabled = disabled;
    if (disabled || this.loading || this.loadFailed) {
      this.selection.disable({emitEvent: false});
    } else {
      this.selection.enable({emitEvent: false});
    }
  }

  validate(control: AbstractControl): ValidationErrors | null {
    if (this.loading || this.loadFailed) {
      return {roomsUnavailable: true};
    }
    if (this.selection.invalid) {
      return {roomNotFound: true};
    }
    return control.value == null ||
      this.rooms.some((room) => room[this.valueField] === control.value)
      ? null
      : {roomNotFound: true};
  }

  registerOnValidatorChange(fn: () => void): void {
    this.onValidatorChange = fn;
  }
}
