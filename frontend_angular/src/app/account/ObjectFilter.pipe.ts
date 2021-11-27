import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'ObjectFilter'
})
export class ObjectFilterPipe implements PipeTransform {

  transform(value: any, filter: any, shouldApply: boolean): any {
    if (!value || !filter || !shouldApply) {
      return value;
    }
    return value.filter(item => {
      for (const [key, _] of Object.entries(filter)) {
        if (!item.hasOwnProperty(key) || item[key] !== filter[key]) { return false; }
      }
      return true;
    });
  }

}
