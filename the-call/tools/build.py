"""Writes index.html for "The Call" from tools/timeline.py. Re-run after any timing change."""
import json
from pathlib import Path

from timeline import GAMES, LENGTH, LINES, NAMES, TAIL

ROOT = Path(__file__).resolve().parent.parent
L = {l[0]: dict(zip(("id", "who", "start", "dur", "ms", "layout", "cap"), l)) for l in LINES}

html = []
js = []
track = {"n": 1}


def r(x):
    return round(x, 3)


def add(s):
    html.append(s)


def tw(s):
    js.append(s)


# ---------------------------------------------------------------- anchor footage
PIP = dict(left=120, top=300, w=288, h=384)
for l in LINES:
    lid, start, dur, ms, lay = l[0], l[2], l[3], l[4], l[5]
    d = TAIL.get(lid, dur)
    if lay == "full":
        style = "left:0;top:0;width:1080px;height:1920px"
    elif lay == "pip":
        style = f"left:{PIP['left']}px;top:{PIP['top']}px;width:{PIP['w']}px;height:{PIP['h']}px"
        add(f'<div id="pipf-{lid}" class="clip pipframe" data-start="{r(start)}" data-duration="{r(dur)}" data-track-index="4" style="z-index:11"><div class="piptag mono">{NAMES[l[1]][0].split()[0]}</div></div>')
    elif lay == "top":
        style = "left:0;top:0;width:1080px;height:960px"
    else:
        style = "left:0;top:960px;width:1080px;height:960px"
    z = 12 if lay == "pip" else 10
    add(f'<video id="v-{lid}" class="clip foot" src="assets/footage/{lid}.mp4" data-start="{r(start)}" data-duration="{r(d)}" data-media-start="{r(ms)}" data-has-audio="true" data-volume="1" data-track-index="{2 if l[1] == 'aditya' else 3}" playsinline style="{style};z-index:{z}"></video>')

# ---------------------------------------------------------------- broadcast furniture (0–5.2)
add('<div id="live" class="clip" data-start="0" data-duration="20.8" data-track-index="5" style="z-index:30">'
    '<div id="liveIn"><span id="livePill" class="mono"><i id="liveDot"></i>LIVE</span><span id="liveCh" class="mono">NXT SPORTS · DELHI</span></div></div>')
for lid, t0 in (("A1", 0.25), ("V1", 2.2)):
    name, sub = NAMES[L[lid]["who"]]
    add(f'<div id="name-{lid}" class="clip namestrap" data-start="{t0}" data-duration="1.6" data-track-index="6" style="z-index:31">'
        f'<div class="nsIn" id="nsIn-{lid}"><div class="nsName disp">{name}</div><div class="nsSub mono">{sub}</div></div></div>')
    tw(f'tl.fromTo("#nsIn-{lid}",{{x:-60,opacity:0}},{{x:0,opacity:1,duration:0.22,ease:"power3.out"}},{t0});')
    tw(f'tl.to("#nsIn-{lid}",{{x:-40,opacity:0,duration:0.15,ease:"power2.in"}},{r(t0 + 1.42)});')
add('<div id="breaking" class="clip" data-start="0.35" data-duration="4.85" data-track-index="7" style="z-index:31">'
    '<div id="brkA" class="disp">BREAKING NEWS</div><div id="brkB" class="disp">NXT ARRIVES IN DELHI</div></div>')
tw('tl.fromTo("#brkA",{scaleX:0},{scaleX:1,duration:0.25,ease:"power4.out"},0.35);')
tw('tl.fromTo("#brkB",{scaleX:0},{scaleX:1,duration:0.28,ease:"power4.out"},0.5);')
tw('tl.to(["#brkA","#brkB"],{x:-900,duration:0.25,ease:"power3.in",stagger:0.05},4.9);')
tick = " · ".join(["NXT ESPORTS ARENA OPENS IN DELHI", "EA SPORTS FC", "VALORANT", "COUNTER-STRIKE 2", "ROCKET LEAGUE",
                        "BGMI", "CALL OF DUTY", "TEKKEN 8", "TOURNAMENTS", "LEAGUES", "COMMUNITY", "@NXT._ESPORTS"]) + " · "
add(f'<div id="ticker" class="clip" data-start="0.35" data-duration="4.85" data-track-index="8" data-layout-ignore style="z-index:31"><div id="tickIn" class="mono">{tick * 2}</div></div>')
tw('tl.fromTo("#tickIn",{x:0},{x:-1500,duration:4.85,ease:"none"},0.35);')
tw('tl.fromTo("#liveDot",{opacity:1},{opacity:0.15,duration:0.4,ease:"none",repeat:25,yoyo:true},0);')

# ---------------------------------------------------------------- captions on talking-head lines
for l in LINES:
    lid, start, dur, cap = l[0], l[2], l[3], l[6]
    if not cap:
        continue
    words = cap.split()
    groups = [" ".join(words[i:i + 3]) for i in range(0, len(words), 3)]
    if len(groups) > 1 and len(groups[-1].split()) == 1:
        last = groups.pop()
        groups[-1] += " " + last
    t0, t1 = start + 0.15, start + dur - 0.05
    step = (t1 - t0) / len(groups)
    for gi, g in enumerate(groups):
        gs = t0 + gi * step
        cid = f"cap-{lid}-{gi}"
        fs = min(70, int(700 / (len(g) * 0.44)))
        add(f'<div id="{cid}" class="clip cap" data-start="{r(gs)}" data-duration="{r(step)}" data-track-index="9" style="z-index:40"><span id="{cid}-t" class="capt disp" style="font-size:{fs}px">{g}</span></div>')
        tw(f'tl.fromTo("#{cid}-t",{{scale:0.86,opacity:0}},{{scale:1,opacity:1,duration:0.09,ease:"back.out(2.4)"}},{r(gs)});')

# ---------------------------------------------------------------- "N-X-T" letters 5.2–5.8, logo slam 5.8–6.4
add('<div id="nxtL" class="clip" data-start="5.2" data-duration="0.6" data-track-index="7" style="z-index:32">'
    '<span id="nl1" class="disp chrome nl">N</span><span id="nl2" class="disp nl red">X</span><span id="nl3" class="disp chrome nl">T</span></div>')
for i, t in enumerate((5.2, 5.36, 5.52)):
    tw(f'tl.fromTo("#nl{i + 1}",{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:0.12,ease:"power4.out"}},{t});')
add('<video id="v-slam" class="clip" src="assets/footage/logo-end.mp4" data-start="5.8" data-duration="0.6" data-media-start="0.1" muted playsinline data-track-index="4" style="left:0;top:0;width:1080px;height:1920px;z-index:50"></video>')

# ---------------------------------------------------------------- roll call 6.4–14.8
for gi, (lid, plate, lines, tag) in enumerate(GAMES):
    s, d = L[lid]["start"], L[lid]["dur"]
    sid = f"g{gi + 1}"
    top = 930 if len(lines) == 2 else 1010
    parts = []
    y = top
    for li, txt in enumerate(lines):
        size = min(300, int(760 / (len(txt) * 0.47)))
        parts.append(f'<div id="{sid}t{li}" class="abs disp gtitle{" chrome" if li == 0 else ""}" style="top:{y}px;font-size:{size}px">{txt}</div>')
        y += int(size * 0.86)
    parts.append(f'<div id="{sid}tag" class="abs mono gtag" style="top:{y + 18}px"><i class="tick"></i>{tag}</div>')
    add(f'<section id="{sid}" class="clip scene" data-start="{r(s)}" data-duration="{r(d)}" data-track-index="1" style="z-index:5">'
        f'<div class="in ink"><div class="plate" id="{sid}p"><img src="assets/games/plates/916/{plate}.jpg" alt="" /></div>'
        f'<div class="layer scrim-t"></div><div class="layer scrim-b"></div>'
        f'<div class="gslash" id="{sid}sl"></div>{"".join(parts)}</div></section>')
    tw(f'tl.fromTo("#{sid}p",{{scale:1.16}},{{scale:1.0,duration:{d},ease:"power2.out"}},{r(s)});')
    tw(f'tl.fromTo("#{sid}sl",{{x:-1400}},{{x:1400,duration:0.3,ease:"power2.inOut"}},{r(s)});')
    for li in range(len(lines)):
        tw(f'tl.fromTo("#{sid}t{li}",{{x:{-90 if li % 2 == 0 else 90},opacity:0}},{{x:0,opacity:1,duration:0.18,ease:"power4.out"}},{r(s + 0.04 + li * 0.06)});')
    tw(f'tl.fromTo("#{sid}tag",{{opacity:0,y:12}},{{opacity:1,y:0,duration:0.15,ease:"power2.out"}},{r(s + 0.2)});')

# ---------------------------------------------------------------- pitch 14.8–20.8
p0, p1 = L["V6"]["start"], L["A8"]["start"] + L["A8"]["dur"]
strips = "".join(
    f'<div class="strip" id="st{i}" style="left:{round(i * 1080 / 7, 2)}px"><img src="assets/games/plates/916/{p}.jpg" alt="" style="left:{-round(i * 1080 / 7, 2)}px" /></div>'
    for i, p in enumerate(("01", "03", "04", "05", "06", "07", "08")))
words = [("pw1", "ONE ARENA.", L["V6"]["start"], 740, 170, "chrome"), ("pw2", "TOURNAMENTS", L["A7"]["start"], 920, 118, ""),
         ("pw3", "LEAGUES", L["V7"]["start"], 1030, 118, ""), ("pw4", "COMMUNITY.", L["A8"]["start"], 1140, 118, "red")]
add(f'<section id="pitch" class="clip scene ink" data-start="{p0}" data-duration="{r(p1 - p0)}" data-track-index="1" style="z-index:5">'
    f'<div class="in"><div id="strips" class="layer" data-layout-allow-overflow>{strips}</div><div class="layer" id="pdim"></div>'
    + "".join(f'<div id="{w}" class="abs disp pword {c}" style="top:{t}px;font-size:{fs}px">{txt}</div>' for w, txt, _, t, fs, c in words)
    + '</div></section>')
for i in range(7):
    tw(f'tl.fromTo("#st{i}",{{y:{-1920 if i % 2 else 1920}}},{{y:0,duration:0.35,ease:"power4.out"}},{r(p0 + i * 0.03)});')
for w, _, t, _, _, _ in words:
    tw(f'tl.fromTo("#{w}",{{y:60,opacity:0,scale:1.15}},{{y:0,opacity:1,scale:1,duration:0.2,ease:"power4.out"}},{r(t + 0.05)});')

# ---------------------------------------------------------------- the joke 20.8–24.8
add('<div id="chat" class="clip" data-start="21.3" data-duration="3.5" data-track-index="7" style="z-index:33">'
    '<div id="chatIn"><div id="chatAv">M</div><div id="chatBody"><div id="chatHead"><b>Mummy</b><span>now</span></div>'
    '<div id="chatMsg">Khana lag gaya hai. Kahan ho?</div><div id="chatSeen" class="mono">SEEN 9:42 PM</div></div></div></div>')
tw('tl.fromTo("#chatIn",{y:-260,opacity:0},{y:0,opacity:1,duration:0.3,ease:"back.out(1.6)"},21.3);')
tw('tl.fromTo("#chatSeen",{opacity:0},{opacity:1,duration:0.05},22.8);')
tw('tl.fromTo("#chatIn",{x:0},{x:14,duration:0.05,ease:"none",repeat:5,yoyo:true},22.8);')
tw('tl.to("#chatIn",{y:-300,opacity:0,duration:0.2,ease:"power2.in"},24.55);')

# ---------------------------------------------------------------- sign-off 24.8–27.2
for sid, lid, a, b, cls in (("so1", "V9", "EVERY", "GAME.", "chrome"), ("so2", "A10", "YOUR", "ESPORTS.", "red")):
    s, d = L[lid]["start"], L[lid]["dur"]
    add(f'<div id="{sid}" class="clip soff" data-start="{s}" data-duration="{d}" data-track-index="7" style="z-index:32">'
        f'<div class="layer scrim-b"></div><div id="{sid}a" class="abs disp sow chrome" style="top:820px">{a}</div>'
        f'<div id="{sid}b" class="abs disp sow {cls}" style="top:1040px">{b}</div></div>')
    tw(f'tl.fromTo("#{sid}a",{{scale:1.4,opacity:0}},{{scale:1,opacity:1,duration:0.16,ease:"power4.out"}},{r(s + 0.05)});')
    tw(f'tl.fromTo("#{sid}b",{{scale:1.4,opacity:0}},{{scale:1,opacity:1,duration:0.16,ease:"power4.out"}},{r(s + 0.25)});')

# ---------------------------------------------------------------- unison split 27.2–28.4
add('<div id="seam" class="clip" data-start="27.2" data-duration="1.2" data-track-index="7" style="z-index:32">'
    '<div id="seamBar"></div><div id="seamTxt" class="disp">N-X-T.</div><div id="seamCap" class="disp capt">THE NEXT ARENA IS HERE.</div></div>')
tw('tl.fromTo("#seamBar",{scaleX:0},{scaleX:1,duration:0.2,ease:"power4.out"},27.2);')
tw('tl.fromTo("#seamTxt",{scale:1.5,opacity:0},{scale:1,opacity:1,duration:0.15,ease:"power4.out"},27.3);')
tw('tl.fromTo("#seamCap",{opacity:0,y:20},{opacity:1,y:0,duration:0.15,ease:"power2.out"},27.75);')

# ---------------------------------------------------------------- end card 28.4–30.4
add(f'<video id="v-end" class="clip" src="assets/footage/logo-end.mp4" data-start="28.4" data-duration="{r(LENGTH - 28.4)}" data-media-start="0.4" muted playsinline data-track-index="4" style="left:0;top:0;width:1080px;height:1920px;z-index:50"></video>')
add(f'<div id="handle" class="clip mono" data-start="28.9" data-duration="{r(LENGTH - 28.9)}" data-track-index="7" style="z-index:51">FOLLOW @NXT._ESPORTS</div>')
tw('tl.fromTo("#handle",{opacity:0,y:16},{opacity:1,y:0,duration:0.25,ease:"power2.out"},28.9);')
add(f'<div id="grain" class="clip layer" data-start="0" data-duration="{LENGTH}" data-track-index="10" data-layout-ignore style="z-index:90"></div>')

# ---------------------------------------------------------------- sound
add(f'<audio id="bed" src="assets/music/call-bed.mp3" data-start="0" data-duration="{LENGTH}" data-track-index="20" data-volume="0.24"></audio>')
add('<audio id="sfx-impact" src="assets/sfx/impact.mp3" data-start="5.8" data-duration="1.6" data-track-index="21" data-volume="0.5"></audio>')
for gi, (lid, *_r) in enumerate(GAMES):
    f = "whoosh-1" if gi % 2 == 0 else "whoosh-2"
    add(f'<audio id="sfx-w{gi}" src="assets/sfx/{f}.mp3" data-start="{r(L[lid]["start"] - 0.08)}" data-duration="0.5" data-media-start="0.05" data-track-index="22" data-volume="0.28"></audio>')
add('<audio id="sfx-chat" src="assets/sfx/whoosh-2.mp3" data-start="21.25" data-duration="0.5" data-track-index="22" data-volume="0.3"></audio>')
add('<audio id="sfx-end" src="assets/sfx/whoosh-1.mp3" data-start="28.32" data-duration="0.5" data-track-index="22" data-volume="0.35"></audio>')

CSS = (ROOT / "tools/style.css").read_text()
page = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>NXT — The Call (intro reel)</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
{CSS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{LENGTH}" data-fps="30" data-width="1080" data-height="1920">
      <div id="bg" class="layer ink"></div>
      {chr(10).join("      " + h for h in html).lstrip()}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in js).lstrip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(page)
print("wrote index.html", len(html), "elements", len(js), "tweens")
