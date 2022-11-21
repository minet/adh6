import { ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { Port, PortService } from '../../api';
import { takeWhile } from 'rxjs/operators';
import { NotificationService } from '../../notification.service';

interface PortForm {
  portNumber: FormControl<number>; 
  roomNumber: FormControl<number>;
}

@Component({
  standalone: true,
  imports: [ReactiveFormsModule],
  selector: 'app-port-new',
  template: `
    <h1 class="title is-1">Création d'un port</h1>
    <form [formGroup]="portForm" (ngSubmit)="onSubmit()" novalidate>
      <div class="field">
        <label>Numero du port</label>
        <input class="input is-fullwidth" formControlName="portNumber" type="text"/>
      </div>
      <div class="field">
        <label>Numero de chambre</label>
        <input class="input is-fullwidth" formControlName="roomNumber" type="number"/>
      </div>
      <div class="field">
        <button type="submit" [disabled]="portForm.status === 'INVALID'" class="button is-primary is-fullwidth">
          Créer
        </button>
      </div>
    </form>
  `
})
export class PortNewComponent implements OnInit {

  portForm: FormGroup<PortForm>;
  switch_id: number;
  private alive = true;

  constructor(
    private fb: FormBuilder,
    public portService: PortService,
    private router: Router,
    private notificationService: NotificationService,
    private route: ActivatedRoute,
  ) {
    this.createForm();
  }

  createForm() {
    this.portForm = this.fb.group({
      roomNumber: [0, [Validators.required]],
      portNumber: [0, [Validators.required]],
    });
  }

  onSubmit() {
    const v = this.portForm.value;
    const port = {
      portNumber: "" + v.portNumber,
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
