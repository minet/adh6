import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'DeviceType'
})
export class DeviceTypePipe implements PipeTransform {

  transform(value: any, args?: any): any {
    if (!value || !args) {
      return value;
    }
    return value.filter(item => item.connectionType === args.connectionType);
  }

}
