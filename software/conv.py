import sys

out = ["{{< myitem"]
nextdesc = True
for line in sys.stdin:
    if line.startswith("--"):
        continue
    elif line.startswith("title"):
        out.append('title="{}"'.format(line[6:].strip().strip('"')))
    elif line.startswith("image"):
        out.append('image="{}"'.format(line[6:].strip().strip('"')))
    elif line.startswith("description"):
        nextdesc = True
    elif nextdesc:
        out.append('description="{}"'.format(line.strip().strip('"')))
        nextdesc = False
    elif line.startswith("external_link"):
        out.append('link="{}"'.format(line[15:].strip().strip('"')))

out.append(">}}")

print(" ".join(out) +"\n")
