#!/usr/bin/env python3
"""xml_parse - Simple XML parser and builder (no dependencies)."""
import sys, re

class XMLNode:
    def __init__(self, tag, attrs=None, children=None, text=""):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = children or []
        self.text = text

    def find(self, tag):
        for c in self.children:
            if c.tag == tag:
                return c
        return None

    def find_all(self, tag):
        return [c for c in self.children if c.tag == tag]

    def get_text(self):
        if self.text:
            return self.text
        return "".join(c.get_text() for c in self.children)

    def to_xml(self, indent=0):
        sp = "  " * indent
        attrs_str = "".join(f' {k}="{v}"' for k, v in self.attrs.items())
        if not self.children and not self.text:
            return f"{sp}<{self.tag}{attrs_str}/>"
        inner = ""
        if self.text:
            inner = self.text
        elif self.children:
            inner = "\n" + "\n".join(c.to_xml(indent + 1) for c in self.children) + f"\n{sp}"
        return f"{sp}<{self.tag}{attrs_str}>{inner}</{self.tag}>"

def parse_xml(text):
    text = text.strip()
    if text.startswith("<?"):
        text = text[text.index("?>") + 2:].strip()
    return _parse_element(text, 0)[0]

def _parse_element(text, pos):
    while pos < len(text) and text[pos].isspace():
        pos += 1
    assert text[pos] == "<"
    pos += 1
    tag_end = pos
    while text[tag_end] not in (" ", ">", "/"):
        tag_end += 1
    tag = text[pos:tag_end]
    pos = tag_end
    attrs = {}
    while pos < len(text) and text[pos] not in (">", "/"):
        if text[pos].isspace():
            pos += 1
            continue
        m = re.match(r'(\w+)="([^"]*)"', text[pos:])
        if m:
            attrs[m.group(1)] = m.group(2)
            pos += m.end()
        else:
            pos += 1
    if text[pos:pos+2] == "/>":
        return XMLNode(tag, attrs), pos + 2
    pos += 1  # skip >
    children = []
    text_content = []
    while pos < len(text):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if text[pos:pos+2] == "</":
            close_end = text.index(">", pos)
            pos = close_end + 1
            node = XMLNode(tag, attrs, children, "".join(text_content).strip())
            return node, pos
        if text[pos] == "<":
            child, pos = _parse_element(text, pos)
            children.append(child)
        else:
            j = pos
            while j < len(text) and text[j] != "<":
                j += 1
            text_content.append(text[pos:j])
            pos = j
    return XMLNode(tag, attrs, children, "".join(text_content).strip()), pos

def test():
    xml = '<root><item id="1">Hello</item><item id="2">World</item></root>'
    doc = parse_xml(xml)
    assert doc.tag == "root"
    assert len(doc.children) == 2
    assert doc.children[0].attrs["id"] == "1"
    assert doc.children[0].text == "Hello"
    items = doc.find_all("item")
    assert len(items) == 2
    first = doc.find("item")
    assert first.text == "Hello"
    empty = parse_xml("<empty/>")
    assert empty.tag == "empty"
    assert empty.children == []
    nested = parse_xml("<a><b><c>deep</c></b></a>")
    assert nested.find("b").find("c").text == "deep"
    out = doc.to_xml()
    assert "<root>" in out
    assert 'id="1"' in out
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("xml_parse: XML parser. Use --test")
