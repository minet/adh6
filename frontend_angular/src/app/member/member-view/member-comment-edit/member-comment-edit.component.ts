import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Comment, MemberService } from '../../../api';
import { NotificationService } from '../../../notification.service';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

interface CommentForm {
  comment: FormControl<string>;
}

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  selector: 'app-member-comment-edit',
  templateUrl: './member-comment-edit.component.html',
})
export class MemberCommentEditComponent implements OnInit {

  constructor(
    private fb: FormBuilder,
    public memberService: MemberService,
    private notificationService: NotificationService,
    private router: Router,
    private route: ActivatedRoute
  ) { }

  public memberComment: FormGroup<CommentForm>;
  private memberId: number;

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.memberId = +params['member_id'];
    });
    this.createForm();
  }

  createForm(): void {
    this.memberComment= this.fb.group({
      comment: ['']
    });
      this.memberService.memberIdCommentGet(this.memberId).subscribe(comment => {
        this.memberComment.controls.comment.setValue(comment.comment);
      });
  }

  changeComment(): void {
    const com = <Comment>{
      comment: this.memberComment.value.comment
    };
    this.memberService.memberIdCommentPut(this.memberId, com).subscribe(() => {
        this.notificationService.successNotification("Comment updated");
        this.router.navigate(['/member/view', this.memberId]);
      });
  }

}
