import {Component, ChangeDetectionStrategy, ViewEncapsulation, Input, EventEmitter, Output} from '@angular/core';


@Component({
  selector: 'app-custom-pagination',
  templateUrl: './custom-pagination.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None
})
export class CustomPaginationComponent {
  @Input() id: string;
  @Output() changePage: EventEmitter<number> = new EventEmitter<number>();
}

