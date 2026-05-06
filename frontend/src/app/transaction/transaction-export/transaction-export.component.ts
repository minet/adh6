import {Component} from "@angular/core";
import {CommonModule} from "@angular/common";
import {FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators} from "@angular/forms";
import {TreasuryService} from "../../api";
import {NotificationService} from "../../notification.service";

interface ExportForm {
  fromDate: FormControl<string>;
  toDate: FormControl<string>;
}

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  selector: "app-transaction-export",
  templateUrl: "./transaction-export.component.html",
})
export class TransactionExportComponent {
  public exportForm: FormGroup<ExportForm>;
  public loading = false;

  constructor(
    private readonly fb: FormBuilder,
    private readonly treasuryService: TreasuryService,
    private readonly notificationService: NotificationService,
  ) {
    const today = new Date().toISOString().slice(0, 10);
    const firstOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
      .toISOString()
      .slice(0, 10);

    this.exportForm = this.fb.group<ExportForm>({
      fromDate: this.fb.control(firstOfMonth, {nonNullable: true, validators: [Validators.required]}),
      toDate: this.fb.control(today, {nonNullable: true, validators: [Validators.required]}),
    });
  }

  public onExport(): void {
    const {fromDate, toDate} = this.exportForm.value;
    if (!fromDate || !toDate) return;

    this.loading = true;
    this.treasuryService.exportTransactions(fromDate, toDate).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `transactions_${fromDate}_${toDate}.ods`;
        a.click();
        URL.revokeObjectURL(url);
        this.loading = false;
      },
      error: () => {
        this.notificationService.errorNotification(500, "Erreur", "Échec de l'export");
        this.loading = false;
      },
    });
  }
}
