import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { map, Observable, switchMap } from 'rxjs';
import { AbstractMember, AbstractRoom, RoomMembersService, RoomService } from '../../../api';
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
    private notificationService: NotificationService,
    public roomService: RoomService,
    public roomMemberService: RoomMembersService
  ) {
    this.refreshRoom();
  }

  public refreshRoom(): void {
    this.room$ = this.memberDetailService.member$
      .pipe(
        switchMap(member => this.roomMemberService.roomMemberIdGet(member.id)
          .pipe(
            switchMap(roomNumber => this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{ roomNumber: roomNumber })
              .pipe(map(rooms => rooms[0]))
            )
          )
        )
      )
  }

  collapseMoveIn(): void {
    this.moveIn = !this.moveIn;
  }

  submitRoom(member: AbstractMember): void {
    this.roomService.roomGet(1, 0, undefined, <AbstractRoom>{ roomNumber: this.roomForm.value.roomNumber })
      .subscribe(rooms => {
        if (rooms.length === 0) {
          this.notificationService.errorNotification(
            404,
            'No Room',
            'There is no room with this number'
          )
          return;
        }
        this.roomMemberService.roomIdMemberPost(rooms[0].id, { id: member.id }).subscribe(() => {
          this.refreshRoom();
          this.collapseMoveIn();
          this.memberDetailService.updateMemberInfos.emit("Chambre mise à jour");
        });
      });
  }
}
