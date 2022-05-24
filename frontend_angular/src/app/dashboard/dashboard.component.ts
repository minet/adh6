import { Component, OnInit, ViewChild } from '@angular/core';
import { Member } from '../api';
import { LOCALE_ID, Inject } from '@angular/core';
import { map, Observable } from 'rxjs';
import { ListComponent } from '../member-device/list/list.component';
import { SessionService } from '../session.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  @ViewChild(ListComponent) wiredList: ListComponent;
  @ViewChild(ListComponent) wirelessList: ListComponent;

  date = new Date();
  isDepartureDateFuture = false;
  isAssociationMode = false;
  member$: Observable<Member>;
  currentTab = "device";

  constructor(
    private sessionService: SessionService,
    @Inject(LOCALE_ID) public locale: string
  ) { }

  ngOnInit() {
    this.member$ = this.sessionService.getUser()
      .pipe(map(member => {
        console.log(member);
        this.isDepartureDateFuture = new Date() < new Date(member.departureDate);
        this.isAssociationMode = new Date() < new Date(member.associationMode);
        return member;
      }));
  }
}
