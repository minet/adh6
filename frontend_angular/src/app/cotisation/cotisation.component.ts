import { Component, OnInit } from '@angular/core';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';
import {AbstractDevice, AbstractMember, Device, DeviceService, Member, MemberService, Room} from '../api';
import {ActivatedRoute} from '@angular/router';

@Component({
  selector: 'app-cotisation',
  templateUrl: './cotisation.component.html',
  styleUrls: ['./cotisation.component.css']
})
export class CotisationComponent implements OnInit {
  constructor(public deviceService: DeviceService,
              public memberService: MemberService,
              ) { }

  ngOnInit() {
  }
}
