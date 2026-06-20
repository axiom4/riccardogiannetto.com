"""
Custom Python-Markdown extension that converts fenced mermaid code blocks
    ```mermaid
    graph TD ...
    ```
into <div class="mermaid">...</div> so that the Mermaid.js library can
render them in the Martor live preview and in the frontend.

Uses a Postprocessor (works on the final HTML string) because the built-in
fenced_code extension stashes blocks before the element tree is built,
making Treeprocessors unable to see them.
"""
import re
from html import unescape

from markdown import Extension
from markdown.postprocessors import Postprocessor

_MERMAID_RE = re.compile(
    r'<pre[^>]*>\s*<code[^>]*class="[^"]*\blanguage-mermaid\b[^"]*"[^>]*>(.*?)</code>\s*</pre>',
    re.DOTALL,
)


def _replace_mermaid(match):
    code = match.group(1)
    # Unescape HTML entities produced by fenced_code.
    code = unescape(code)
    return f'<div class="mermaid">{code}</div>'


class MermaidPostprocessor(Postprocessor):
    def run(self, text):
        return _MERMAID_RE.sub(_replace_mermaid, text)


class MermaidExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(MermaidPostprocessor(md), 'mermaid', 5)


def makeExtension(**kwargs):
    return MermaidExtension(**kwargs)
