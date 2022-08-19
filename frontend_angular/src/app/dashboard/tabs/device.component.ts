import { Component, Input, ViewChild } from '@angular/core';
import { AbstractDevice } from '../../api';
import { ListComponent } from '../../member-device/list/list.component';

@Component({
  selector: 'app-device',
  template: `
    <app-device-new [member_id]="memberId"
      (added)="$event.connectionType === 'wired' ? wiredList.updateSearch() : wirelessList.updateSearch()">
    </app-device-new>
    <br />
    <div class="content">
      <div class="columns">
        <div class="column has-text-centered">
          <h4 class="title is-4" i18n="@@wired">Filaire</h4>
          <app-member-device-list #wiredList [abstractDeviceFilter]="wiredDeviceFilter"></app-member-device-list>
        </div>
        <div class="column has-text-centered">
          <h4 class="title is-4" i18n="@@wireless">Wifi</h4>
          <app-member-device-list #wirelessList [abstractDeviceFilter]="wirelessDeviceFilter"></app-member-device-list>
        </div>
      </div>
      <div class="notification is-warning">
        <h4 class="title is-4" i18n="dashboard help problem|Is the user encountering any issue ?">Un problème ?</h4>
        <ol class="text-left">
          <li i18n="help tutorials|Has the user taken a look at the tutorials ?">
            Avez-vous bien regardé
            <a class="alert-link" href="//www.minet.net/fr/tutoriels.html" i18n-href="url tutorials">
              les tutoriels
            </a>
            ?
          </li>
          <li i18n="help tickets|The user may send a ticket">
            Envoyez-nous <a class="alert-link" href="//tickets.minet.net/?lang=fr" i18n-href="url tickets">un ticket</a>
          </li>
          <li i18n="help helpdesk|The user may come see us directly">
            Éventuellement, passez au local pendant
            <a class="alert-link" href="//www.minet.net/fr/" i18n-href="url minet">une des permanences</a> !
          </li>
        </ol>
      </div>
    </div>
  `,
})
export class DeviceComponent {
  @Input() memberId: number;

  @ViewChild(ListComponent) wiredList: ListComponent;
  @ViewChild(ListComponent) wirelessList: ListComponent;

  get wiredDeviceFilter(): AbstractDevice {
    return {
      member: this.memberId,
      connectionType: 'wired'
    }
  }

  get wirelessDeviceFilter(): AbstractDevice {
    return {
      member: this.memberId,
      connectionType: 'wireless'
    }
  }

  constructor() { }
}
