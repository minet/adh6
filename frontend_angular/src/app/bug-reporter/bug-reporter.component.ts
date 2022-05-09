import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { faBug } from '@fortawesome/free-solid-svg-icons';
import { BugReport, MiscService } from '../api';
import { NotificationService } from '../notification.service';

@Component({
  selector: 'app-bug-reporter',
  templateUrl: './bug-reporter.component.html',
  styleUrls: ['./bug-reporter.component.sass']
})
export class BugReporterComponent implements OnInit {
  faBug = faBug;
  submitBugForm: FormGroup;
  bugModal: boolean = false;

  constructor(
    private notificationService: NotificationService,
    private miscService: MiscService,
    private fb: FormBuilder,
  ) {
    this.createForm();
  }

  ngOnInit(): void {
  }

  public toogleModal(): void {
    this.bugModal = !this.bugModal;
  }

  createForm() {
    this.submitBugForm = this.fb.group({
      bugTitle: ['', Validators.required],
      bugDescription: ['', Validators.required]
    });
  }

  onSubmitBug() {
    const bugReport: BugReport = {
      title: this.submitBugForm.value.bugTitle,
      description: this.submitBugForm.value.bugDescription,
      labels: [],
    };

    this.miscService.bugReportPost(bugReport)
      .subscribe(_ => {
        this.submitBugForm.reset();
        this.notificationService.successNotification('Ok!', 'Bug envoyé avec succès ');
      });
  }
}
