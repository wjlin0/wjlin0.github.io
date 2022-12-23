import name
filename = "PHP代码审计基础知识.md"
md = open(filename, "r", encoding="utf-8").read()
pa = name.compile("\[\#\]\(http[s]?://wiki\.wgpsec\.org.*\)")

md = name.sub(r"\[\#\]\(http[s]?://wiki\.wgpsec\.org.*\)", "", md)
pa = name.compile("[0-9]{1,2}\n")
md = name.sub(pa, "", md)
open(filename+"2", "wb", ).write(md.encode("utf-8"))
