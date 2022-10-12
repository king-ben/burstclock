import sys
from pathlib import Path
import lxml.etree as etree

parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)

chunk = b""
before_start = True
for line in (Path(__file__).parent / "template.md").open("rb"):
    if b"```xml" in line:
        if before_start:
            chunk = b""
            line = line[line.index(b"```xml") + 6 :]
            continue
        else:
            line = line.replace(b"```xml", b"-->")
    elif b"```" in line:
        parser.feed(chunk)
        chunk = b""
        line = line.replace(b"```", b"<!--")
    chunk = chunk + line


et = parser.close().getroottree()

et.write(open(sys.argv[1], "wb"), pretty_print=True, xml_declaration=True, encoding=et.docinfo.encoding)
