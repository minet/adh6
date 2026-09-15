import {Component, DestroyRef, OnInit} from "@angular/core";
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";
import {Observable} from "rxjs";
import {MemberService, AbstractMember} from "../../api";
import {ActivatedRoute, RouterModule} from "@angular/router";
import {map, switchMap} from "rxjs/operators";
import {CommonModule} from "@angular/common";
import {MemberDetailService} from "./member-detail.service";
import {NotificationService} from "../../notification.service";

@Component({
  imports: [CommonModule, RouterModule],
  selector: "app-view",
  templateUrl: "./view.component.html",
})
export class ViewComponent implements OnInit {
  public currentTab = "profile";
  public member$!: Observable<AbstractMember>;

  constructor(
    public memberService: MemberService,
    private readonly route: ActivatedRoute,
    private readonly memberDetailService: MemberDetailService,
    private readonly notificationService: NotificationService,
    private readonly destroyRef: DestroyRef,
  ) {}

  ngOnInit() {
    this.refreshInfo();
    this.memberDetailService.updateMemberInfos
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((msg: string) => {
        this.refreshInfo();
        this.notificationService.successNotification(
          $localize`:@@member.updated:Adhérent mis à jour`,
          msg,
        );
      });
  }

  refreshInfo(): void {
    this.member$ = this.route.params.pipe(
      switchMap((params) =>
        this.memberService.memberIdGet(params["member_id"]),
      ),
      map((member) => {
        this.memberDetailService.refreshMember(member);
        return member;
      }),
    );
  }
}
