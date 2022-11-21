import { EventEmitter, Injectable } from '@angular/core';
import { BehaviorSubject, shareReplay } from 'rxjs';
import { AbstractMember } from '../../api';

@Injectable({
  providedIn: 'root'
})
export class MemberDetailService {
  private memberSource = new BehaviorSubject<AbstractMember>(null);

  public updateMemberInfos = new EventEmitter<string>();
  public member$ = this.memberSource.asObservable().pipe(shareReplay(1));
  
  public refreshMember(member: AbstractMember) {
    this.memberSource.next(member);
  }
}
