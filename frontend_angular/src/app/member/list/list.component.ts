import { Component, OnInit } from '@angular/core';
import { map, Observable, shareReplay } from 'rxjs';
import { MemberService, AbstractMember } from '../../api';
import { SearchPage } from '../../search-page';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent extends SearchPage<number> implements OnInit {
  public cachedMembers: Map<Number, Observable<AbstractMember>> = new Map();

  constructor(
    public memberService: MemberService,
  ) {
    super((terms, page) => this.memberService.memberGet(this.itemsPerPage, (page - 1) * this.itemsPerPage, terms, undefined, "response")
      .pipe(
        map(response => {
          for (let i of response.body) {
            console.log(i);
            this.cachedMembers.set(+i, this.memberService.memberIdGet(+i)
              .pipe(
                shareReplay(1)
              )
            );
            console.log(this.cachedMembers)
          }
          return response
        }),
      ));
  }
  //  
  ngOnInit() {
    super.ngOnInit();
  }

  handlePageChange(page: number) {
    this.changePage(page);
  }

  public getMember(id: number) {
    console.log(this.cachedMembers.has(id));
    return this.cachedMembers.get(id)
  }
}
