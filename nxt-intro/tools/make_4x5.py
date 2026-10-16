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
      #c1a { top: 350px !important; }
      #c1b { top: 562px !important; }
      #c2n { top: 200px !important; font-size: 720px !important; }
      #c2v { top: 1210px !important; width: 1000px !important; }
      #c2t { font-size: 196px !important; }
      #c3t { top: 558px !important; }
      #c4band { top: 530px !important; }
      #c5a { top: 417px !important; }
      #c5b { top: 676px !important; }
      #c6t { top: 508px !important; }
      #c7n { top: 182px !important; font-size: 720px !important; }
      #c7v { top: 110px !important; width: 1000px !important; }
      #c7t { font-size: 196px !important; }
      #c8n { top: 160px !important; font-size: 900px !important; }
      #c8band { top: 550px !important; }
      #wall { top: -1025px !important; }
      #headline { top: 300px !important; }
    </style>"""
s = s.replace("    </style>", OVR, 1)
out = root / "variants/4x5"
out.mkdir(parents=True, exist_ok=True)
(out / "index.html").write_text(s)
link = out / "assets"
if not link.exists():
    link.symlink_to("../../assets")
for f in ("hyperframes.json", "meta.json"):
    (out / f).write_text((root / f).read_text())
print("wrote", out / "index.html")
