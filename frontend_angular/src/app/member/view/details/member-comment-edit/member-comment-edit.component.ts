import {Component} from "@angular/core";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
} from "@angular/forms";
import {MemberService} from "../../../../api";
import {Router, RouterModule} from "@angular/router";
import {CommonModule, Location} from "@angular/common";
import {MemberDetailService} from "../../member-detail.service";
import {map, Observable} from "rxjs";

interface CommentForm {
  comment: FormControl<string>;
}

@Component({
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  selector: "app-member-comment-edit",
  templateUrl: "./member-comment-edit.component.html",
})
export class MemberCommentEditComponent {
  public memberComment: FormGroup<CommentForm>;
  public memberId$: Observable<number>;

  constructor(
    private readonly fb: FormBuilder,
    public memberService: MemberService,
    private readonly memberDetailService: MemberDetailService,
    private readonly router: Router,
  ) {
    this.memberComment = this.fb.group({
      comment: this.fb.control("", {nonNullable: true}),
    });
    this.memberId$ = this.memberDetailService.member$.pipe(
      map((member) => {
        if (member?.id != null) {
          this.memberService.memberIdCommentGet(member.id).subscribe({
            next: (comment) =>
              this.memberComment.controls.comment.setValue(
                comment.comment || "",
              ),
            error: (error) =>
              console.error("Error fetching member comment:", error),
          });
          return member.id;
        }
        return 0; // fallback value
      }),
    );
  }

  update(id: number): void {
    if (this.memberComment.controls.comment.dirty) {
      const commentValue = this.memberComment.value.comment;
      if (commentValue != null) {
        this.memberService
          .memberIdCommentPut(id, {comment: commentValue})
          .subscribe({
            next: () =>
              this.memberDetailService.updateMemberInfos.emit(
                "Comment updated",
              ),
            error: (error) =>
              console.error("Error updating member comment:", error),
          });
      }
    }
    void this.router.navigate(["/member/view", id, "profile"]);
  }
}
