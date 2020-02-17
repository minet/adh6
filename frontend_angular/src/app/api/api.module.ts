import { NgModule, ModuleWithProviders, SkipSelf, Optional } from '@angular/core';
import { Configuration } from './configuration';
import { HttpClient } from '@angular/common/http';


import { AccountService } from './api/account.service';
import { DeviceService } from './api/device.service';
import { MemberService } from './api/member.service';
import { MembershipService } from './api/membership.service';
import { MiscService } from './api/misc.service';
import { Oauth2Service } from './api/oauth2.service';
import { PortService } from './api/port.service';
import { RoomService } from './api/room.service';
import { SwitchService } from './api/switch.service';
import { TransactionService } from './api/transaction.service';
import { TreasuryService } from './api/treasury.service';

@NgModule({
  imports:      [],
  declarations: [],
  exports:      [],
  providers: [
    AccountService,
    DeviceService,
    MemberService,
    MembershipService,
    MiscService,
    Oauth2Service,
    PortService,
    RoomService,
    SwitchService,
    TransactionService,
    TreasuryService ]
})
export class ApiModule {
    public static forRoot(configurationFactory: () => Configuration): ModuleWithProviders {
        return {
            ngModule: ApiModule,
            providers: [ { provide: Configuration, useFactory: configurationFactory } ]
        };
    }

    constructor( @Optional() @SkipSelf() parentModule: ApiModule,
                 @Optional() http: HttpClient) {
        if (parentModule) {
            throw new Error('ApiModule is already loaded. Import in your base AppModule only.');
        }
        if (!http) {
            throw new Error('You need to import the HttpClientModule in your AppModule! \n' +
            'See also https://github.com/angular/angular/issues/20575');
        }
    }
}
