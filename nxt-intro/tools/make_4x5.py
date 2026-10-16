"""Derive the 4:5 feed cut (1080x1350) from index.html by re-flowing layouts, not cropping."""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
s = (root / "index.html").read_text()
for a, b in [('data-resolution="portrait"', 'data-resolution="custom"'),
             ('content="width=1080, height=1920"', 'content="width=1080, height=1350"'),
             ('height: 1920px;\n        overflow: hidden;\n        background: var(--ink);\n      }\n      #root', 'height: 1350px;\n        overflow: hidden;\n        background: var(--ink);\n      }\n      #root'),
             ('data-height="1920"', 'data-height="1350"'),
             ("<title>NXT — Brand Intro 10s</title>", "<title>NXT — Brand Intro 10s · 4:5</title>")]:
    assert a in s, a
    s = s.replace(a, b)
OVR = """
      /* ===== 4:5 re-flow (1080x1350) ===== */
      #hookPlaneA, #hookPlaneB { height: 2150px !important; }
      #hookEvery { top: 630px !important; font-size: 300px !important; }
      #hookGame { top: 1200px !important; font-size: 300px !important; }
      #hookSlash { top: 668px !important; }
      .l3 { top: 1180px !important; }
      #c1a { top: 712px !important; font-size: 170px !important; }
      #c1b { top: 876px !important; font-size: 300px !important; }
      #c2n { top: 790px !important; font-size: 420px !important; }
      #c2v { top: 1150px !important; width: 1040px !important; height: 180px !important; }
      #c2t { font-size: 182px !important; line-height: 180px !important; }
      #c3t { top: 900px !important; font-size: 256px !important; }
      #c4band { top: 760px !important; }
      #c5a { top: 720px !important; font-size: 250px !important; }
      #c5b { top: 916px !important; font-size: 250px !important; }
      #c6t { top: 740px !important; font-size: 500px !important; }
      #c7n { top: 790px !important; font-size: 420px !important; }
      #c7v { top: 110px !important; width: 1040px !important; height: 180px !important; }
      #c7t { font-size: 182px !important; line-height: 180px !important; }
      #c8band { top: 850px !important; }
      #wall { top: -1025px !important; }
      #headline { top: 300px !important; }
    </style>"""
s = s.replace("    </style>", OVR, 1)
s = s.replace("assets/games/plates/916/", "assets/games/plates/45/")
out = root / "variants/4x5"
out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(s)
link = out / "assets"
if not link.exists():
    link.symlink_to("../../assets")
for f in ("hyperframes.json", "meta.json"):
    (out / f).write_text((root / f).read_text())
print("wrote", out / "index.html")
