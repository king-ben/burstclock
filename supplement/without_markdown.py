from pathlib import Path

import lxml.etree as etree

parser = etree.XMLParser()

chunk = ""
before_start = True
for line in open(Path(__file__) / "template.md"):
    if "```xml" in line:
        if before_start:
            chunk = ""
            line = line[line.index("```xml") + 6 :]
            before_start = False
        else:
            line = line.replace("```xml", "-->")
    if "```" in line:
        parser.feed(chunk)
        chunk = ""
        line = line.replace("```", "<!--")
    chunk = chunk + line


root = parser.close()

print(etree.tostring(root, pretty_print=True).decode("utf-8"))
