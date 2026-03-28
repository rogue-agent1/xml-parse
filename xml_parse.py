#!/usr/bin/env python3
"""XML parser, formatter, and XPath-like query tool."""
import sys, xml.etree.ElementTree as ET, json

def to_dict(elem):
    d = {'tag': elem.tag}
    if elem.attrib: d['attrs'] = dict(elem.attrib)
    if elem.text and elem.text.strip(): d['text'] = elem.text.strip()
    children = [to_dict(c) for c in elem]
    if children: d['children'] = children
    return d

def query(root, path):
    results = root.findall(path)
    for r in results:
        text = r.text.strip() if r.text else ''
        attrs = ' '.join(f'{k}="{v}"' for k,v in r.attrib.items())
        print(f"<{r.tag}{' '+attrs if attrs else ''}> {text}")
    return results

def fmt(filename, indent=2):
    ET.indent(ET.parse(filename).getroot(), space=' '*indent)
    ET.dump(ET.parse(filename).getroot())

if __name__ == '__main__':
    if len(sys.argv) < 2: print("Usage: xml_parse.py <file.xml> [json|query <xpath>|format]"); sys.exit(1)
    if len(sys.argv) == 2 or sys.argv[2] == 'json':
        tree = ET.parse(sys.argv[1])
        print(json.dumps(to_dict(tree.getroot()), indent=2))
    elif sys.argv[2] == 'query':
        tree = ET.parse(sys.argv[1])
        query(tree.getroot(), sys.argv[3])
    elif sys.argv[2] == 'format':
        tree = ET.parse(sys.argv[1])
        ET.indent(tree.getroot())
        ET.dump(tree.getroot())
