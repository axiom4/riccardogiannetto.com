import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'marked',
  standalone: true,
})
export class MarkedPipe implements PipeTransform {
  async transform(
    value: string | null | undefined,
  ): Promise<string | null | undefined> {
    if (value && value.length > 0) {
      const { marked } = await import('marked');
      return marked(value) as string;
    }
    return value;
  }
}
