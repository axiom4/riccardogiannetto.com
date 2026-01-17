import { MarkedPipe } from './marked.pipe';

describe('MarkedPipe', () => {
  it('create an instance', () => {
    const pipe = new MarkedPipe();
    expect(pipe).toBeTruthy();
  });

  it('transforms markdown to html', async () => {
    const pipe = new MarkedPipe();
    const markdown = '# Hello';
    const html = await pipe.transform(markdown);
    expect(html).toContain('<h1>Hello</h1>');
  });
});
