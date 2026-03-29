#!/usr/bin/env python3
"""XML parser — SAX-style events and DOM tree building."""
import re, sys

class XMLNode:
    def __init__(self, tag, attrs=None):
        self.tag = tag; self.attrs = attrs or {}; self.children = []; self.text = ""
    def find(self, tag):
        for c in self.children:
            if c.tag == tag: return c
        return None
    def find_all(self, tag): return [c for c in self.children if c.tag == tag]
    def __repr__(self): return f"<{self.tag}{' ...' if self.attrs else ''}>{len(self.children)} children"

class XMLParser:
    def parse(self, xml):
        xml = re.sub(r'<\?.*?\?>', '', xml).strip()
        return self._parse_element(xml, 0)[0]
    def _parse_attrs(self, s):
        attrs = {}
        for m in re.finditer(r'(\w+)=["\'](.*?)["\'\"]', s):
            attrs[m.group(1)] = m.group(2)
        return attrs
    def _parse_element(self, xml, pos):
        m = re.match(r'<(\w+)(\s[^>]*)?\/>', xml[pos:])
        if m:
            tag = m.group(1); attrs = self._parse_attrs(m.group(2) or "")
            return XMLNode(tag, attrs), pos + m.end()
        m = re.match(r'<(\w+)(\s[^>]*)?>', xml[pos:])
        if not m: return None, pos
        tag = m.group(1); attrs = self._parse_attrs(m.group(2) or "")
        node = XMLNode(tag, attrs); pos += m.end()
        while pos < len(xml):
            close = re.match(r'</' + tag + r'\s*>', xml[pos:])
            if close: pos += close.end(); return node, pos
            child_match = re.match(r'<\w', xml[pos:])
            if child_match:
                child, pos = self._parse_element(xml, pos)
                if child: node.children.append(child)
            else:
                end = xml.find('<', pos)
                if end == -1: node.text += xml[pos:]; break
                node.text += xml[pos:end]; pos = end
        return node, pos

if __name__ == "__main__":
    xml = """<library>
  <book id="1" genre="fiction">
    <title>The Great Gatsby</title>
    <author>F. Scott Fitzgerald</author>
    <year>1925</year>
  </book>
  <book id="2" genre="science">
    <title>A Brief History of Time</title>
    <author>Stephen Hawking</author>
    <year>1988</year>
  </book>
</library>"""
    parser = XMLParser(); root = parser.parse(xml)
    print(f"Root: {root}")
    for book in root.find_all("book"):
        title = book.find("title"); author = book.find("author")
        print(f"  [{book.attrs.get('genre')}] {title.text if title else '?'} by {author.text if author else '?'}")
