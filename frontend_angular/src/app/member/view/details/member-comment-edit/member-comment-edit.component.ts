import { Component } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MemberService } from '../../../../api';
import { Router, RouterModule } from '@angular/router';
import { CommonModule, Location } from '@angular/common';
import { MemberDetailService } from '../../member-detail.service';
import { map, Observable } from 'rxjs';

interface CommentForm {
  comment: FormControl<string>;
}

@Component({
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  selector: 'app-member-comment-edit',
  templateUrl: './member-comment-edit.component.html',
})
export class MemberCommentEditComponent {
  public memberComment: FormGroup<CommentForm>;
  public memberId$: Observable<number>;

  constructor(
    private fb: FormBuilder,
    public memberService: MemberService,
    private memberDetailService: MemberDetailService,
    private router: Router,
  ) {
    this.memberComment = this.fb.group({
      comment: ['']
    });
    this.memberId$ = this.memberDetailService.member$
      .pipe(map(member => {
        this.memberService.memberIdCommentGet(member.id).subscribe(comment => this.memberComment.controls.comment.setValue(comment.comment));
        return member.id;
      }))
  }

  update(id: number): void {
    if (this.memberComment.controls.comment.dirty) {
      this.memberService.memberIdCommentPut(id, {comment: this.memberComment.value.comment})
        .subscribe(() => this.memberDetailService.updateMemberInfos.emit("Comment updated"));
    }
    this.router.navigate(['/member/view', id, 'profile'])
  }
}
