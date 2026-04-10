import {Component, OnInit} from "@angular/core";
import {AsyncPipe} from "@angular/common";
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
  ReactiveFormsModule,
} from "@angular/forms";
import {ActivatedRoute, ParamMap, Router} from "@angular/router";

import {AbstractRoom, RoomService} from "../../api";
import {finalize, switchMap, tap} from "rxjs/operators";
import {Observable} from "rxjs";
import {NotificationService} from "../../notification.service";

@Component({
  imports: [AsyncPipe, ReactiveFormsModule],
  selector: "app-room-edit",
  templateUrl: "./room-edit.component.html",
  styleUrls: ["./room-edit.component.css"],
  standalone: true,
})
export class RoomEditComponent implements OnInit {
  public disabled = false;
  public roomEdit!: UntypedFormGroup;
  public room$!: Observable<AbstractRoom>;

  constructor(
    private readonly roomService: RoomService,
    private readonly fb: UntypedFormBuilder,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly notificationService: NotificationService,
  ) {
    this.createForm();
  }

  createForm() {
    this.disabled = false;
    this.roomEdit = this.fb.group({
      id: ["", [Validators.required]],
      roomNumber: [
        "",
        [Validators.min(0), Validators.max(9999), Validators.required],
      ],
      vlan: ["", [Validators.min(41), Validators.max(49), Validators.required]],
      description: ["", Validators.required],
    });
  }

  onSubmit() {
    const v = this.roomEdit.value;
    this.disabled = true;
    const room: AbstractRoom = {
      roomNumber: v.roomNumber,
      vlan: v.vlan,
      description: v.description,
    };
    this.roomService
      .roomIdPut(v.id, room)
      .pipe(finalize(() => (this.disabled = false)))
      .subscribe(() => {
        void this.router.navigate(["/room/view", v.id]);
        this.notificationService.successNotification();
      });
  }

  ngOnInit() {
    this.room$ = this.route.paramMap.pipe(
      switchMap((params: ParamMap) => {
        const roomId = params.get("room_id");
        if (roomId) {
          return this.roomService.roomIdGet(+roomId);
        }
        throw new Error("Room ID parameter is required");
      }),
      tap((room) =>
        this.roomEdit.patchValue({
          id: room.id,
          roomNumber: room.roomNumber,
          description: room.description,
          vlan: room.vlan,
        }),
      ),
    );
  }
}
