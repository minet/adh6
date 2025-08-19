import {Component, OnInit} from "@angular/core";
import {RouterModule} from "@angular/router";
import {ReactiveFormsModule} from "@angular/forms";
import {AsyncPipe} from "@angular/common";
import {PaginationComponent} from "../../pagination/pagination.component";
import {AbstractSwitch, SwitchService} from "../../api";
import {SearchPage} from "../../search-page";

@Component({
  imports: [RouterModule, ReactiveFormsModule, AsyncPipe, PaginationComponent],
  selector: "app-switch-list",
  templateUrl: "./switch-list.component.html",
  styleUrls: ["./switch-list.component.css"],
  standalone: true,
})
export class SwitchListComponent
  extends SearchPage<AbstractSwitch>
  implements OnInit
{
  constructor(public switchService: SwitchService) {
    super((terms, page) =>
      this.switchService.switchGet(
        this.itemsPerPage,
        (page - 1) * this.itemsPerPage,
        terms,
        undefined,
        ["ip", "description"],
        "response",
      ),
    );
  }

  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }
}
