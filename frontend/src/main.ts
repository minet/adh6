import {enableProdMode, importProvidersFrom} from "@angular/core";
import {bootstrapApplication} from "@angular/platform-browser";

import {AppComponent} from "./app/app.component";
import {AppModule} from "./app/app.module";
import {environment} from "./environments/environment";

if (environment.production) {
  enableProdMode();
}

bootstrapApplication(AppComponent, {
  providers: [importProvidersFrom(AppModule)],
}).catch((err) => console.log(err));
