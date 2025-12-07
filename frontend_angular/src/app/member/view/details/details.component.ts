import {CommonModule} from "@angular/common";
import {Component} from "@angular/core";
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import {RouterModule} from "@angular/router";
import {map, Observable, switchMap} from "rxjs";
import {
  AbstractMember,
  AbstractRoom,
  RoomMembersService,
  RoomService,
} from "../../../api";
import {MailinglistComponent} from "../../../mailinglist/mailinglist.component";
import {NotificationService} from "../../../notification.service";
import {MemberDetailService} from "../member-detail.service";

interface RoomForm {
  roomNumber: FormControl<number | null>;
}

@Component({
  imports: [
    CommonModule,
    RouterModule,
    MailinglistComponent,
    ReactiveFormsModule,
  ],
  selector: "app-details",
  templateUrl: "./details.component.html",
})
export class DetailsComponent {
  public moveIn = false;
  public roomForm: FormGroup<RoomForm> = new FormGroup({
    roomNumber: new FormControl<number | null>(null, Validators.required),
  });
  public room$!: Observable<AbstractRoom>;

  constructor(
    public memberDetailService: MemberDetailService,
    private readonly notificationService: NotificationService,
    public roomService: RoomService,
    public roomMemberService: RoomMembersService,
  ) {
    this.refreshRoom();
  }

  public refreshRoom(): void {
    this.room$ = this.memberDetailService.member$.pipe(
      switchMap((member) => {
        if (member?.id != null) {
          return this.roomMemberService
            .roomMemberIdGet(member.id)
            .pipe(switchMap((roomId) => this.roomService.roomIdGet(roomId)));
        }
        throw new Error("Member ID is required");
      }),
    );
  }

  collapseMoveIn(): void {
    this.moveIn = !this.moveIn;
  }

  submitRoom(member: AbstractMember): void {
    const roomNumber = this.roomForm.value.roomNumber;
    if (roomNumber == null) {
      this.notificationService.errorNotification(
        400,
        "Invalid Room Number",
        "Please enter a valid room number",
      );
      return;
    }

    this.roomService
      .roomGet(1, 0, undefined, <AbstractRoom>{
        roomNumber: roomNumber,
      })
      .subscribe((rooms) => {
        if (rooms.length === 0) {
          this.notificationService.errorNotification(
            404,
            "No Room",
            "There is no room with this number",
          );
          return;
        }

        if (rooms[0].id != null && member.id != null) {
          this.roomMemberService
            .roomIdMemberPost(rooms[0].id, {id: member.id})
            .subscribe(() => {
              this.refreshRoom();
              this.collapseMoveIn();
              this.memberDetailService.updateMemberInfos.emit(
                "Chambre mise à jour",
              );
            });
        }
      });
  }
}
