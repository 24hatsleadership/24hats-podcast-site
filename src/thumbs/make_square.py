"""Square (1080x1080) episode covers for Substack. usage: python make_square.py OUTDIR [ep ...]"""
import json, os, sys, html
from playwright.sync_api import sync_playwright
import make_thumbs as T
esc = html.escape
def card(r, head, guest, fs):
    sub = f"with {esc(guest)}" if guest else T.host_line(r)
    return f"""<style>*{{box-sizing:border-box;margin:0}}body{{width:1080px;height:1080px;overflow:hidden;background:#141118;color:#f3f1f8;font-family:Inter,'Helvetica Neue',Arial,sans-serif;position:relative}}
.glow{{position:absolute;right:-260px;top:-260px;width:1000px;height:1000px;border-radius:50%;background:radial-gradient(circle,rgba(97,51,126,.8),transparent 68%)}}
.num{{position:absolute;right:20px;top:-60px;font-size:560px;line-height:1;font-weight:900;letter-spacing:-.05em;color:transparent;-webkit-text-stroke:3px rgba(167,123,199,.5)}}
.ep{{position:absolute;left:80px;top:80px;font-size:28px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#a77bc7}}
.panel{{position:absolute;left:0;right:0;bottom:0;height:560px;background:#61337e;padding:56px 80px 0 80px}}
h1{{font-size:{fs}px;line-height:1.06;font-weight:800;letter-spacing:-.02em}}.sub{{margin-top:24px;font-size:36px;font-weight:700;color:#cfe4fb}}
.logo{{position:absolute;height:54px;left:80px;bottom:44px}}</style>
<div class="glow"></div><div class="num">{r['ep']}</div><div class="ep">Episode {r['ep']}</div><div class="panel"><h1>{esc(head)}</h1><div class="sub">{sub}</div></div><img class="logo" src="{T.LOGO}">"""
if __name__ == "__main__":
    out = sys.argv[1]; only = {int(x) for x in sys.argv[2:]}; os.makedirs(out, exist_ok=True)
    data = json.load(open(os.path.join(T.SRC, "data", "episodes_pages.json")))
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1080})
        for r in data:
            if only and r["ep"] not in only: continue
            head, guest = T.split(r); fs = 76
            while True:
                pg.set_content(f"<!doctype html><html><body>{card(r, head, guest, fs)}</body></html>"); pg.wait_for_timeout(80)
                bottom = pg.evaluate("(()=>{const h=document.querySelector('h1').getBoundingClientRect(), s=document.querySelector('.sub').getBoundingClientRect(); return s.bottom})()")
                if bottom <= 960 or fs <= 40: break
                fs -= 4
            pg.screenshot(path=os.path.join(out, f"ep{r['ep']:02d}.png"))
