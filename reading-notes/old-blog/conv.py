import sys

def do_file(name):
    to_print = []
    to_print.append("---")

    in_head = 0
    for line in open(name + "/index.md"):
        line = line.strip()
        if in_head > 1:
            to_print.append(line)
        if line == "---":
            if in_head == 1:
                to_print.append('aliases: [ "/post/{}/", ]'.format(name.lower()))
                to_print.append("---")
            in_head += 1
        elif line.startswith("title"):
            to_print.append("title: {}".format(line[7:].strip()))
        elif line.startswith("summary"):
            to_print.append("description: {}".format(line[9:].strip()))

    out = open(name + "/index.md", 'w')
    print("\n".join(to_print), file=out)
    out.close()

for line in sys.stdin:
    for part in line.strip().split():
        part = part[:-9]
        do_file(part)
