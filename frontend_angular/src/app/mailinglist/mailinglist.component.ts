import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { AbstractMember, MemberService } from '../api';
import { NotificationService } from '../notification.service';

@Component({
  selector: 'app-mailinglist',
  templateUrl: './mailinglist.component.html',
  styleUrls: ['./mailinglist.component.scss']
})
export class MailinglistComponent implements OnInit {
  @Input() mailinglistValue: number;
  @Input() memberId: number;
  @Output() udpatedMailinglistValue: EventEmitter<number> = new EventEmitter<number>();

  public mailMiNET: boolean = false;
  public mailHosting: boolean = false;
  public mailRouteur: boolean = false;

  constructor(
    private memberService: MemberService,
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
    this.memberService.memberIdPatch(<AbstractMember>{ mailinglist: newValue }, this.memberId)
      .subscribe(
        () => {
          this.udpatedMailinglistValue.emit(newValue);
          this.notificationService.successNotification("mailing list updated");
        }
      )
  }
}
