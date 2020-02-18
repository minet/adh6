import {ActivatedRoute, Router} from '@angular/router';
import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {NotificationsService} from 'angular2-notifications';
import {Port, PortService} from '../api';
import {takeWhile} from 'rxjs/operators';

@Component({
  selector: 'app-port-new',
  templateUrl: './port-new.component.html',
  styleUrls: ['./port-new.component.css']
})
export class PortNewComponent implements OnInit {

  portForm: FormGroup;
  switch_id: number;
  private alive = true;
  private sub: any;

  constructor(
    private fb: FormBuilder,
    public portService: PortService,
    private router: Router,
    private notif: NotificationsService,
    private route: ActivatedRoute,
  ) {
    this.createForm();
  }

  createForm() {
    this.portForm = this.fb.group({
      id: ['', [Validators.required]],
      roomNumber: ['', [Validators.required]],
      portNumber: ['', [Validators.required]],

    });
  }

  onSubmit() {
    const v = this.portForm.value;
    const port: Port = {
      id: v.id,
      portNumber: v.portNumber,
      room: v.roomNumber,
      _switch: this.switch_id
    };
    this.portService.portPost(port)
      .pipe(takeWhile(() => this.alive))
      .subscribe((res) => {
        this.router.navigate(['/switch/', this.switch_id, 'details']);
        this.notif.success('Success');
      });
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.switch_id = +params['switch_id'];
    });
  }

}
