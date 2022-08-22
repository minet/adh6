import { ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { Port, PortService } from '../../api';
import { takeWhile } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';

@Component({
  selector: 'app-port-new',
  templateUrl: './port-new.component.html',
  styleUrls: ['./port-new.component.css']
})
export class PortNewComponent implements OnInit {

  portForm: UntypedFormGroup;
  switch_id: number;
  private alive = true;

  constructor(
    private fb: UntypedFormBuilder,
    public portService: PortService,
    private router: Router,
    private notificationService: NotificationService,
    private route: ActivatedRoute,
  ) {
    this.createForm();
  }

  createForm() {
    this.portForm = this.fb.group({
      roomNumber: ['', [Validators.required]],
      portNumber: ['', [Validators.required]],

    });
  }

  onSubmit() {
    const v = this.portForm.value;
    const port = {
      portNumber: v.portNumber,
      room: v.roomNumber,
      switchObj: this.switch_id
    };

    this.portService.portPost(port)
      .pipe(takeWhile(() => this.alive))
      .subscribe((res: Port) => {
        this.router.navigate(['/switch/', this.switch_id, '/port/', res.id]);
        this.notificationService.successNotification();
      });
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.switch_id = +params['switch_id'];
    });
  }

}
