import re
filename = "PHP代码审计基础知识.md"
md = open(filename, "r", encoding="utf-8").read()
pa = re.compile("\[\#\]\(http[s]?://wiki\.wgpsec\.org.*\)")

md = re.sub(r"\[\#\]\(http[s]?://wiki\.wgpsec\.org.*\)", "", md)
pa = re.compile("[0-9]{1,2}\n")
md = re.sub(pa, "", md)
open(filename+"2", "wb", ).write(md.encode("utf-8"))
