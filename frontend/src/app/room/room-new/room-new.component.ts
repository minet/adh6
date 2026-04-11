import {Component, OnInit} from "@angular/core";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import {Router} from "@angular/router";
import {finalize} from "rxjs/operators";

import {Room, RoomService} from "../../api";
import {NotificationService} from "../../notification.service";

@Component({
  imports: [ReactiveFormsModule],
  selector: "app-room-new",
  templateUrl: "./room-new.component.html",
  styleUrls: ["./room-new.component.css"],
  standalone: true,
})
export class RoomNewComponent implements OnInit {
  public disabled = false;
  public roomForm!: UntypedFormGroup;

  constructor(
    private readonly roomService: RoomService,
    private readonly fb: UntypedFormBuilder,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
  ) {}

  ngOnInit() {
    this.createForm();
  }

  createForm() {
    this.roomForm = this.fb.group({
      roomNumber: [
        "",
        [Validators.min(1000), Validators.max(9999), Validators.required],
      ],
      vlan: ["", [Validators.min(41), Validators.max(49), Validators.required]],
      description: ["", Validators.required],
    });
  }

  onSubmit() {
    this.disabled = true;
    const v = this.roomForm.value;
    const room: Room = {
      roomNumber: v.roomNumber,
      vlan: v.vlan,
      description: v.description,
    };

    this.roomService
      .roomPost(room)
      .pipe(finalize(() => (this.disabled = false)))
      .subscribe({
        next: (createdRoom) => {
          const id = createdRoom.id ?? v.roomNumber;
          void this.router.navigate(["/room/view", id]);
          this.notificationService.successNotification();
        },
        error: (err: {status: number}) => {
          this.notificationService.errorNotification(err.status);
        },
      });
  }
}
