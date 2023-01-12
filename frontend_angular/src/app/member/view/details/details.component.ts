import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { AbstractMember, AbstractRoom, Member, RoomMembersService, RoomService } from '../../../api';
import { MailinglistComponent } from '../../../mailinglist/mailinglist.component';
import { NotificationService } from '../../../notification.service';
import { MemberDetailService } from '../member-detail.service';

interface RoomForm {
  roomNumber: FormControl<number>
}

@Component({
  standalone: true,
  imports: [CommonModule, RouterModule, MailinglistComponent, ReactiveFormsModule],
  selector: 'app-details',
  templateUrl: './details.component.html'
})
export class DetailsComponent {
  public moveIn: boolean = false;
  private roomForm: FormGroup<RoomForm> = new FormGroup({
    roomNumber: new FormControl(null, Validators.required)
  });
  public room$: Observable<AbstractRoom>;

  constructor(
    public memberDetailService: MemberDetailService,
    public roomService: RoomService,
    public roomMemberService: RoomMembersService
  ) {
    this.refreshRoom();
  }

  public refreshRoom(): void {
    this.room$ = this.memberDetailService.member$.pipe(
      switchMap(member => this.roomMemberService.roomMemberLoginGet(member.username)),
      switchMap(roomNumber => this.roomService.roomRoomNumberGet(roomNumber))
    );
  }

  collapseMoveIn(): void {
    this.moveIn = !this.moveIn;
  }

  submitRoom(member: AbstractMember): void {
    this.roomMemberService.roomRoomNumberMemberPost(this.roomForm.value.roomNumber, { login: member.username })
      .subscribe(() => {
        this.refreshRoom();
        this.collapseMoveIn();
        this.memberDetailService.updateMemberInfos.emit("Chambre mise à jour");
      });
  }

  public isMembershipValidated(member: Member): boolean {
    return member.membership === 'ABORTED' || member.membership === 'CANCELLED' || member.membership === 'COMPLETE'
  }
}
