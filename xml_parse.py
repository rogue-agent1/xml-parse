#!/usr/bin/env python3
"""xml_parse - Minimal XML parser to dict/JSON."""
import sys,re,json
class XMLNode:
    def __init__(s,tag="",attrs=None):s.tag=tag;s.attrs=attrs or{};s.children=[];s.text=""
    def to_dict(s):
        d={}
        if s.attrs:d["@"+k]=v for k,v in s.attrs.items()
        if s.text.strip():
            if not s.children:return s.text.strip()
        child_d={}
        for c in s.children:
            cd=c.to_dict()
            if c.tag in child_d:
                if not isinstance(child_d[c.tag],list):child_d[c.tag]=[child_d[c.tag]]
                child_d[c.tag].append(cd)
            else:child_d[c.tag]=cd
        return child_d or s.text.strip()
def parse_xml(text):
    text=re.sub(r"<!--.*?-->","",text,flags=re.DOTALL)
    tokens=re.findall(r"<[^>]+>|[^<]+",text)
    stack=[];root=None
    for t in tokens:
        if t.startswith("</"):
            if stack:
                node=stack.pop()
                if stack:stack[-1].children.append(node)
                else:root=node
        elif t.startswith("<"):
            m=re.match(r"<(\w+)(.*?)(/?)>",t,re.DOTALL)
            if m:
                tag=m[1];attrs=dict(re.findall(r'(\w+)=["']([^"']*)["']',m[2]))
                node=XMLNode(tag,attrs)
                if m[3]:
                    if stack:stack[-1].children.append(node)
                    else:root=node
                else:stack.append(node)
        else:
            if stack:stack[-1].text+=t
    return root
if __name__=="__main__":
    if len(sys.argv)<2:text=sys.stdin.read()
    else:text=open(sys.argv[1]).read()
    root=parse_xml(text)
    if root:print(json.dumps({root.tag:root.to_dict()},indent=2))
