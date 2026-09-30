"""Inline data + section images into the app template.

Outputs
  dist/atlas.html  page body only (the format the Artifact publisher wraps)
  dist/index.html  same page with a doctype/head wrapper, for opening locally
Run from the project root:  python3 tools/build_app.py
"""
import base64, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = ROOT / "data"
meta = json.loads((data / "meta.json").read_text())
plans = json.loads((data / "plans.json").read_text())
upper = json.loads((data / "upper.json").read_text())
def jpeg_size(b):
    i = 2
    while i < len(b):
        if b[i] != 0xFF: i += 1; continue
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(b[i + 2:i + 4], "big")

meso = json.loads((data / "meso.json").read_text())
meso["img"], meso["imgSize"] = {}, {}
for f in sorted((data / "meso").glob("*.jpg")):
    raw = f.read_bytes()
    meso["img"][f.stem] = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
    meso["imgSize"][f.stem] = jpeg_size(raw)
sections = ["data:image/png;base64," + base64.b64encode((data / f"p10_{i}.png").read_bytes()).decode() for i in range(8)]

payload = json.dumps({"meta": meta, "plans": plans, "upper": upper, "sections": sections, "meso": meso}, separators=(",", ":"))
page = (ROOT / "src" / "atlas.template.html").read_text().replace("__DATA__", payload)

dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
(dist / "atlas.html").write_text(page)
(dist / "index.html").write_text(
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    "<style>[hidden]{display:none!important}</style></head><body>\n" + page + "\n</body></html>\n"
)
print("wrote", dist / "atlas.html", f"{len(page)/1024:.0f} KB")
