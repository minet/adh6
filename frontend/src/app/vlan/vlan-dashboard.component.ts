import {Component, OnInit} from "@angular/core";
import {AsyncPipe, DecimalPipe, NgClass} from "@angular/common";
import {map, Observable} from "rxjs";
import {VlanStats, VlanService} from "../api";

export interface VlanRow extends VlanStats {
  fillPct: number;
  isOverLimit: boolean;
}

@Component({
  standalone: true,
  selector: "app-vlan-dashboard",
  templateUrl: "./vlan-dashboard.component.html",
  imports: [AsyncPipe, DecimalPipe, NgClass],
})
export class VlanDashboardComponent implements OnInit {
  vlans$!: Observable<VlanRow[]>;

  constructor(private readonly vlanService: VlanService) {}

  ngOnInit() {
    this.vlans$ = this.vlanService.vlansStatsGet().pipe(
      map((vlans) =>
        vlans.map((vlan) => {
          const cap = vlan.capacity ?? null;
          const fillPct =
            cap && cap > 0 ? Math.min(100, (vlan.deviceCount / cap) * 100) : 0;
          return {
            ...vlan,
            fillPct,
            isOverLimit: cap !== null && vlan.deviceCount > cap,
          } as VlanRow;
        }),
      ),
    );
  }

  progressClass(row: VlanRow): string {
    if (row.isOverLimit) return "is-danger";
    if (row.fillPct >= 75) return "is-warning";
    return "is-success";
  }
}
