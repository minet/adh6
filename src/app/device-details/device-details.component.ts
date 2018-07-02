import { Component, OnInit, OnDestroy } from '@angular/core'

import { Observable } from 'rxjs/Observable'

import { DeviceService } from '../api/services/device.service'
import { Device } from '../api/models/device'

import { Router, ActivatedRoute } from '@angular/router'


@Component({
  selector: 'app-device-details',
  templateUrl: './device-details.component.html',
  styleUrls: ['./device-details.component.css']
})
export class DeviceDetailsComponent implements OnInit, OnDestroy {

  device$: Observable<Device>
  mac: string

  constructor( 
    public deviceService: DeviceService, 
    private route: ActivatedRoute,
    private router: Router) { }

  onDelete( mac: string ) {
    this.deviceService.deleteDevice( mac ).first().subscribe( () => {
      this.router.navigate(["device/search"])
    })
  }

  ngOnInit() {
    this.device$ = this.route.params.switchMap( params => {
      this.mac = params["mac"]
      return this.deviceService.getDevice( this.mac )
    })
  }

  ngOnDestroy() {
  }

}
