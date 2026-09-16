import {Component, Input} from "@angular/core";
import {MiniRouterAddresses} from "./addresses";

/** The four addresses derived from the number of a mini-router. */
@Component({
  selector: "app-mini-router-addresses",
  styles: `
    dl {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
      gap: 0.75rem 1.5rem;
      margin: 0;
    }
    dt {
      font-size: 0.75rem;
      color: var(--bulma-text-weak);
    }
    dd {
      margin: 0;
    }
  `,
  template: `
    <dl>
      <div>
        <dt>IP (WG)</dt>
        <dd class="is-family-monospace">{{ addresses.ipWireguard ?? "—" }}</dd>
      </div>
      <div>
        <dt>IP (VLAN31)</dt>
        <dd class="is-family-monospace">{{ addresses.ipVlan31 ?? "—" }}</dd>
      </div>
      <div>
        <dt>MAC (Accept)</dt>
        <dd class="is-family-monospace">{{ addresses.macAccept ?? "—" }}</dd>
      </div>
      <div>
        <dt>MAC (Deny)</dt>
        <dd class="is-family-monospace">{{ addresses.macDeny ?? "—" }}</dd>
      </div>
    </dl>
  `,
})
export class MiniRouterAddressesComponent {
  @Input({required: true}) addresses!: MiniRouterAddresses;
}
