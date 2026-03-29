#!/usr/bin/env python3
"""xml_parse: Minimal XML parser (no dependencies)."""
import re, sys

class Element:
    def __init__(self, tag, attrs=None, children=None, text=""):
        self.tag = tag; self.attrs = attrs or {}
        self.children = children or []; self.text = text

    def find(self, tag):
        for c in self.children:
            if c.tag == tag: return c
        return None

    def find_all(self, tag):
        return [c for c in self.children if c.tag == tag]

    def get(self, attr, default=None):
        return self.attrs.get(attr, default)

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>{self.text}</{self.tag}>"

def parse(xml):
    xml = xml.strip()
    # Remove XML declaration
    xml = re.sub(r'<\?xml[^?]*\?>', '', xml).strip()
    return _parse_element(xml, 0)[0]

def _parse_element(xml, pos):
    # Skip whitespace
    while pos < len(xml) and xml[pos] in ' \t\n\r': pos += 1
    if xml[pos] != '<': raise ValueError(f"Expected '<' at {pos}")
    # Parse opening tag
    end = xml.index('>', pos)
    tag_content = xml[pos+1:end]
    self_closing = tag_content.endswith('/')
    if self_closing: tag_content = tag_content[:-1]
    parts = tag_content.split(None, 1)
    tag = parts[0]
    attrs = {}
    if len(parts) > 1:
        for m in re.finditer(r'(\w+)=["\'](.*?)["\']', parts[1]):
            attrs[m.group(1)] = m.group(2)
    if self_closing:
        return Element(tag, attrs), end + 1
    pos = end + 1
    children = []
    text_parts = []
    while pos < len(xml):
        # Skip whitespace
        while pos < len(xml) and xml[pos] in ' \t\n\r': pos += 1
        if pos >= len(xml): break
        if xml[pos:pos+2] == '</':
            close_end = xml.index('>', pos)
            break
        elif xml[pos] == '<':
            child, pos = _parse_element(xml, pos)
            children.append(child)
        else:
            text_end = xml.index('<', pos)
            text_parts.append(xml[pos:text_end].strip())
            pos = text_end
    else:
        close_end = pos
    text = " ".join(t for t in text_parts if t)
    return Element(tag, attrs, children, text), close_end + 1

def to_xml(elem, indent=0):
    prefix = "  " * indent
    attrs = "".join(f' {k}="{v}"' for k, v in elem.attrs.items())
    if not elem.children and not elem.text:
        return f"{prefix}<{elem.tag}{attrs}/>"
    parts = [f"{prefix}<{elem.tag}{attrs}>"]
    if elem.text: parts.append(f"{prefix}  {elem.text}")
    for c in elem.children:
        parts.append(to_xml(c, indent + 1))
    parts.append(f"{prefix}</{elem.tag}>")
    return "\n".join(parts)

def test():
    xml = '<root><item id="1">Hello</item><item id="2">World</item></root>'
    elem = parse(xml)
    assert elem.tag == "root"
    assert len(elem.children) == 2
    assert elem.children[0].tag == "item"
    assert elem.children[0].attrs["id"] == "1"
    assert elem.children[0].text == "Hello"
    assert elem.find("item").text == "Hello"
    assert len(elem.find_all("item")) == 2
    # Self-closing
    xml2 = '<root><br/><hr/></root>'
    elem2 = parse(xml2)
    assert len(elem2.children) == 2
    assert elem2.children[0].tag == "br"
    # Attributes
    xml3 = '<a href="http://x" class="link">click</a>'
    elem3 = parse(xml3)
    assert elem3.get("href") == "http://x"
    assert elem3.text == "click"
    # to_xml
    output = to_xml(elem)
    assert "<root>" in output
    assert "</root>" in output
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: xml_parse.py test")
