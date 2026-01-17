import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    name: "marked",
    standalone: true,
})
export class MarkedPipe implements PipeTransform {
  async transform(value: any): Promise<any> {
    if (value && value.length > 0) {
      const { marked } = await import('marked');
      return marked(value);
    }
    return value;
  }
}
