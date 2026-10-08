"""Render episode thumbnails from src/data/episodes_pages.json.
usage: python make_thumbs.py STYLE OUTDIR [ep ep ...]   (STYLE: a, b, c; size 1280x720)"""
import json, os, sys, base64, html
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "..")
LOGO = "data:image/png;base64," + base64.b64encode(open(os.path.join(SRC, "brand", "e765a83b-image.png"), "rb").read()).decode()
esc = html.escape

def split(r):
    t = r["title"]
    if r["type"] == "Guest" and ": " in t:
        head, guest = t.rsplit(": ", 1)
        return head, guest
    if r["type"] == "Guest" and " with " in t:
        head, guest = t.rsplit(" with ", 1)
        return head, guest
    return t, None

def initials(g):
    parts = [p for p in g.replace(" and ", " ").split() if p[0].isupper() and not p.endswith(".")]
    return "".join(p[0] for p in parts[:2]) if parts else "24"

BASE = """*{box-sizing:border-box;margin:0}body{width:1280px;height:720px;overflow:hidden;background:#141118;color:#f3f1f8;font-family:Inter,'Helvetica Neue',Arial,sans-serif;position:relative}
.logo{position:absolute;height:54px}.ep{font-weight:800;letter-spacing:.16em;text-transform:uppercase}"""

def style_a(r, head, guest):  # typographic
    fs = 84 if len(head) < 42 else 72 if len(head) < 62 else 62
    g = f'<div style="position:absolute;left:80px;bottom:96px;font-size:40px;font-weight:700;color:#6db0f5">with {esc(guest)}</div>' if guest else '<div style="position:absolute;left:80px;bottom:96px;font-size:34px;font-weight:600;color:#a3b0a0">Jason Kempf</div>'
    return f"""<style>{BASE}
.glow{{position:absolute;right:-200px;top:-220px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(97,51,126,.75),transparent 68%)}}
h1{{position:absolute;left:80px;top:150px;width:1000px;font-size:{fs}px;line-height:1.04;font-weight:800;letter-spacing:-.025em}}
.ep{{position:absolute;left:80px;top:84px;font-size:24px;color:#a77bc7}}.bar{{position:absolute;left:80px;bottom:60px;width:120px;height:5px;background:#a77bc7}}</style>
<div class="glow"></div><div class="ep">Episode {r['ep']}</div><h1>{esc(head)}</h1>{g}<div class="bar"></div><img class="logo" style="right:80px;bottom:56px" src="{LOGO}">"""

def style_b(r, head, guest):  # guest card with initials badge
    fs = 66 if len(head) < 50 else 56
    badge = initials(guest) if guest else "24"
    sub = esc(guest) if guest else "Jason Kempf"
    return f"""<style>{BASE}
body{{background:linear-gradient(135deg,#141118 0%,#1d1923 55%,#2a1a36 100%)}}
.badge{{position:absolute;left:80px;top:120px;width:300px;height:300px;border-radius:50%;background:#61337e;border:6px solid #a77bc7;display:flex;align-items:center;justify-content:center;font-size:120px;font-weight:800;letter-spacing:-.02em}}
.ep{{position:absolute;left:80px;top:468px;font-size:22px;color:#a77bc7}}.name{{position:absolute;left:80px;top:512px;width:360px;font-size:34px;font-weight:700;color:#6db0f5;line-height:1.15}}
h1{{position:absolute;left:470px;top:190px;width:740px;font-size:{fs}px;line-height:1.06;font-weight:800;letter-spacing:-.02em}}
.rule{{position:absolute;left:470px;top:440px;width:120px;height:5px;background:#a77bc7}}</style>
<div class="badge">{esc(badge)}</div><div class="ep">Episode {r['ep']}</div><div class="name">{sub}</div><h1>{esc(head)}</h1><div class="rule"></div><img class="logo" style="right:80px;bottom:56px" src="{LOGO}">"""

def style_c(r, head, guest):  # bold number
    fs = 60 if len(head) < 50 else 52
    sub = f"with {esc(guest)}" if guest else "Jason Kempf"
    return f"""<style>{BASE}
.num{{position:absolute;right:30px;top:-70px;font-size:640px;line-height:1;font-weight:900;letter-spacing:-.05em;color:transparent;-webkit-text-stroke:3px rgba(167,123,199,.55)}}
.panel{{position:absolute;left:0;bottom:0;width:860px;height:430px;background:#61337e;padding:56px 70px 0 80px}}
h1{{font-size:{fs}px;line-height:1.06;font-weight:800;letter-spacing:-.02em}}.sub{{margin-top:26px;font-size:32px;font-weight:700;color:#cfe4fb}}
.ep{{position:absolute;left:80px;top:80px;font-size:24px;color:#a77bc7}}</style>
<div class="num">{r['ep']}</div><div class="ep">Episode {r['ep']}</div><div class="panel"><h1>{esc(head)}</h1><div class="sub">{sub}</div></div><img class="logo" style="right:80px;bottom:56px" src="{LOGO}">"""

STYLES = {"a": style_a, "b": style_b, "c": style_c}
if __name__ == "__main__":
    style, out = sys.argv[1], sys.argv[2]; only = {int(x) for x in sys.argv[3:]}
    os.makedirs(out, exist_ok=True)
    data = json.load(open(os.path.join(SRC, "data", "episodes_pages.json")))
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 720})
        for r in data:
            if only and r["ep"] not in only: continue
            head, guest = split(r)
            pg.set_content(f"<!doctype html><html><body>{STYLES[style](r, head, guest)}</body></html>")
            pg.wait_for_timeout(120)
            pg.screenshot(path=os.path.join(out, f"ep{r['ep']:02d}-{style}.png"))
        b.close()
