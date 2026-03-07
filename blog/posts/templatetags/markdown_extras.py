import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify", is_safe=True)
def markdownify(value: str) -> str:
    """
    Convert a Markdown string to safe HTML.

    Extensions enabled:
    - fenced_code      : ```lang ... ``` blocks
    - codehilite       : Pygments-based syntax highlighting classes (we rely
                          on Highlight.js in the browser instead, but the
                          extension adds language classes to <code> tags)
    - tables           : GFM-style tables
    - toc              : auto heading anchors via [TOC]
    - nl2br            : newline → <br> inside paragraphs
    - attr_list        : {: .class #id } attribute syntax
    - def_list         : definition lists
    - footnotes        : [^1] footnotes
    - admonition       : !!! note / warning / tip blocks
    - sane_lists       : better list handling
    - smarty           : smart quotes / dashes
    - meta             : front-matter style metadata (ignored in output)
    """
    extensions = [
        "fenced_code",
        "tables",
        "toc",
        "nl2br",
        "attr_list",
        "def_list",
        "footnotes",
        "admonition",
        "sane_lists",
        "smarty",
        "meta",
        "codehilite",
    ]

    extension_configs = {
        "codehilite": {
            # We use Highlight.js for actual colour rendering, so just emit
            # plain <code> tags with a language class that hljs can pick up.
            "use_pygments": False,
            "css_class": "hljs",
            "noclasses": False,
        },
        "toc": {
            "permalink": True,
            "permalink_class": "toc-anchor",
            "title": "Table of Contents",
        },
    }

    md = markdown.Markdown(
        extensions=extensions, extension_configs=extension_configs
    )
    html = md.convert(value)
    return mark_safe(html)
