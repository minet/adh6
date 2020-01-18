import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'ObjectFilter'
})
export class ObjectFilterPipe implements PipeTransform {

  transform(value: any, args?: any): any {
    if (!value || !args) {
      return value;
    }
    return value.filter(item => {
      for (const [key, _] of Object.entries(args)) {
        if (!item.hasOwnProperty(key) || item[key] !== args[key]) { return false; }
      }
      return true;
    });
  }

}
