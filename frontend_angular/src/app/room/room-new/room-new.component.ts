import {Component, OnDestroy} from "@angular/core";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import {Router} from "@angular/router";

import {Room, RoomService} from "../../api";
import {takeWhile} from "rxjs/operators";
import {NotificationService} from "../../notification.service";

@Component({
  imports: [ReactiveFormsModule],
  selector: "app-room-new",
  templateUrl: "./room-new.component.html",
  styleUrls: ["./room-new.component.css"],
  standalone: true,
})
export class RoomNewComponent implements OnDestroy {
  disabled = false;
  roomForm!: UntypedFormGroup;
  private alive = true;

  constructor(
    public roomService: RoomService,
    private readonly fb: UntypedFormBuilder,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
  ) {
    this.createForm();
  }

  createForm() {
    this.roomForm = this.fb.group({
      roomNumber: [
        "",
        [Validators.min(1000), Validators.max(9999), Validators.required],
      ],
      vlan: ["", [Validators.min(0), Validators.max(100), Validators.required]],
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
      .pipe(takeWhile(() => this.alive))
      .subscribe((_) => {
        void this.router.navigate(["/room/view", v.roomNumber]);
        this.notificationService.successNotification();
      });
    this.disabled = false;
  }

  ngOnDestroy() {
    this.alive = false;
  }
}
