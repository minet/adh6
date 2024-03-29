import { CommonModule } from '@angular/common';
import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MailinglistService } from '../api';
import { NotificationService } from '../notification.service';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  selector: 'app-mailinglist',
  templateUrl: './mailinglist.component.html'
})
export class MailinglistComponent implements OnInit {
  @Input() mailinglistValue: number;
  @Input() memberId: number;
  @Output() udpatedMailinglistValue: EventEmitter<number> = new EventEmitter<number>();

  public mailMiNET: boolean = false;
  public mailHosting: boolean = false;
  public mailRouteur: boolean = false;

  constructor(
    private mailinglistService: MailinglistService,
    private notificationService: NotificationService
  ) { }

  ngOnInit(): void {
    const decomp = (this.mailinglistValue >>> 0).toString(2);
    this.mailMiNET = decomp.charAt(7) === "1";
    this.mailHosting = decomp.charAt(6) === "1";
    this.mailRouteur = decomp.charAt(5) === "1";
  }

  public updateMailinglist() {
    const newValue = 248 + 4 * (+this.mailRouteur) + 2 * (+this.mailHosting) + 1 * (+this.mailMiNET);
    console.log(newValue);
    console.log(this.mailinglistValue)
    this.mailinglistService.mailinglistMemberIdPut(this.memberId, { value: newValue })
      .subscribe(
        () => {
          this.udpatedMailinglistValue.emit(newValue);
          this.notificationService.successNotification("mailing list updated");
        }
      )
  }
}
