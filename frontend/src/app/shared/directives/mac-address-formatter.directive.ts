import {Directive, ElementRef, HostListener, OnInit} from "@angular/core";
import {NgControl} from "@angular/forms";

@Directive({
  selector: "[appMacAddressFormatter]",
  standalone: true,
})
export class MacAddressFormatterDirective implements OnInit {
  constructor(
    private readonly el: ElementRef,
    private readonly control: NgControl,
  ) {}

  ngOnInit(): void {
    // Set initial styling for better mobile experience
    this.el.nativeElement.style.fontFamily = "monospace";
    this.el.nativeElement.style.textTransform = "uppercase";
    this.el.nativeElement.style.letterSpacing = "0.5px";
  }

  @HostListener("input", ["$event"])
  onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = input.value;

    // Format the MAC address
    const formattedValue = this.formatMacAddress(value);

    // Update the input value
    input.value = formattedValue;

    // Update the form control value
    if (this.control && this.control.control) {
      this.control.control.setValue(formattedValue, {emitEvent: false});
    }

    // Set cursor position after formatting
    this.setCursorPosition(input, formattedValue);
  }

  @HostListener("paste", ["$event"])
  onPaste(event: ClipboardEvent): void {
    event.preventDefault();
    const pastedText = event.clipboardData?.getData("text") || "";
    const formattedValue = this.formatMacAddress(pastedText);

    const input = event.target as HTMLInputElement;
    input.value = formattedValue;

    if (this.control && this.control.control) {
      this.control.control.setValue(formattedValue);
    }
  }

  private formatMacAddress(input: string): string {
    // Remove all non-alphanumeric characters
    let cleaned = input.replace(/[^a-fA-F0-9]/g, "");

    // Convert to uppercase
    cleaned = cleaned.toUpperCase();

    // Limit to 12 characters (6 pairs)
    cleaned = cleaned.substring(0, 12);

    // Add dashes every 2 characters
    const formatted = cleaned.replace(/(.{2})/g, "$1-").replace(/-$/, "");

    return formatted;
  }

  private setCursorPosition(
    input: HTMLInputElement,
    formattedValue: string,
  ): void {
    // Simple cursor positioning - place at end
    // Could be improved to maintain relative position
    setTimeout(() => {
      const position = formattedValue.length;
      input.setSelectionRange(position, position);
    }, 0);
  }
}
