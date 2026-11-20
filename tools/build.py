#!/usr/bin/env python3
"""Build the site.

  python3 tools/build.py                 -> writes index.html (standalone, data inlined)
  python3 tools/build.py --fragment DIR  -> also writes DIR/index.html (head-less page that
                                            fetches questions.json) + DIR/questions.json

src/app.html holds the page: everything above <!--BODY--> goes into <head>,
everything below into <body>. <!--DATA--> marks where the inline data script goes.
"""
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "app.html"
DATA = ROOT / "data" / "questions.json"

RESET = """<style>
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); color-scheme: light; }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }
</style>"""


def main() -> None:
    src = SRC.read_text(encoding="utf-8")
    assert src.count("<!--BODY-->") == 1 and src.count("<!--DATA-->") == 1
    head, body = src.split("<!--BODY-->")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert len(data) == 40
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    inline = f"<script>window.EXAM_DATA={blob};</script>"

    page = (
        "<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        f"{RESET}\n{head.strip()}\n</head>\n<body>\n{body.replace('<!--DATA-->', inline).strip()}\n</body>\n</html>\n"
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("wrote index.html", len(page.encode("utf-8")), "bytes")

    if "--fragment" in sys.argv:
        out = pathlib.Path(sys.argv[sys.argv.index("--fragment") + 1])
        out.mkdir(parents=True, exist_ok=True)
        frag = src.replace("<!--BODY-->\n", "").replace("<!--DATA-->\n", "")
        (out / "index.html").write_text(frag, encoding="utf-8")
        shutil.copyfile(DATA, out / "questions.json")
        print("wrote fragment to", out)


if __name__ == "__main__":
    main()
