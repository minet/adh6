import {
  Directive,
  ElementRef,
  EventEmitter,
  HostListener,
  Output,
} from "@angular/core";

@Directive({
  selector: "[appClickOutside]",
})
export class ClickOutsideDirective {
  constructor(private readonly _elementRef: ElementRef) {}

  @Output()
  public clickOutside = new EventEmitter<MouseEvent>();

  @HostListener("document:click", ["$event", "$event.target"])
  public onClick(event: MouseEvent, targetElement: EventTarget | null): void {
    if (!targetElement) {
      return;
    }

    const clickedInside =
      this._elementRef.nativeElement.contains(targetElement);
    if (!clickedInside) {
      this.clickOutside.emit(event);
    }
  }
}
