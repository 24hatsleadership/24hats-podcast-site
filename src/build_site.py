import json, os, re, shutil, html
from datetime import date
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "dist")
PACK = os.path.join(ROOT, "data", "episodes_pages.json")
UP = os.path.join(ROOT, "brand")
SITE = os.environ.get("SITE_BASE", "https://24hatsleadership.github.io/24hats-podcast-site").rstrip("/")
PODCAST_PAGE = "https://24hatsleadership.substack.com/s/24-hats-leadership-podcast"
YOUTUBE = "https://www.youtube.com/channel/UCubDs-imFumHR6-VOzHVJjw"
CONTACT = "https://24hats.hbportal.co/schedule/6a0f494d615cc6fc9083c3ab"
NAME = "24 Hats Leadership Podcast"
TAG = "People focused leadership in a world of disruption."
esc = html.escape

eps = json.load(open(PACK))
OVER = {
 86:"Few of us enjoy leading through change. Here is how to hold it as both a gift and a responsibility for the people you lead.",
 85:"The last in a four-part series on leader types: what it takes to lead in a way that frees people up.",
 84:"How to spot and step back from domination when deadlines and expectations pile up.",
 83:"The start of a mini-series on four types of leaders, beginning with the protective and supportive leader.",
 70:"How the disruption of recent years exposed what a resilient team needs, and practical ways to build it.",
 68:"Jason and Chris on bringing leadership to the people above you and beside you, not only below you.",
 49:"Best-selling author and entrepreneur Jeremie Kubicek on the Peace Index and being a fountain for the people around you.",
 30:"Jason and Chris on developing your organization through vision, strategy, and core values.",
 87:"Why understanding yourself is where leading others starts.",
 81:"What leadership and service look like in saving lives and serving a community, with Fire Chief Jeremy Pell.",
 79:"Dave Maurer on impact, connecting, and legacy while leading and serving on the Southside of Indy.",
 75:"Jason and Chris talk with Melahni Ake, a podcaster, leadership coach, and speaker, about leading every day.",
}
for _r in eps:
    if _r["ep"] in OVER: _r["summary"] = OVER[_r["ep"]]
eps.sort(key=lambda r: -r["ep"])
by_ep = {r["ep"]: r for r in eps}

def clean(s):
    return (s or "").replace(" — ", ", ").replace("—", ", ").replace("&amp;", "&").strip()

def short(s, n=155):
    s = clean(s)
    if len(s) <= n: return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "..."

def mins(r): return r["minutes"]
def has_body(r): return bool(r["summary"])

CSS = """
:root{--purple:#61337e;--purple-light:#a77bc7;--ink:#f3f1f8;--muted:#b8b2c6;--olive:#a3b0a0;--azure:#6db0f5;--btn:#2585e4;--bg:#141118;--surface:#1d1923;--line:#332c3f;color-scheme:dark}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.6 Inter,"Helvetica Neue",Arial,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
img{max-width:100%;height:auto}a{color:var(--azure);text-underline-offset:3px}a:hover{color:#fff}
.skip{position:absolute;left:-999px;top:0;background:var(--purple);color:#fff;padding:.6rem 1rem;z-index:10}.skip:focus{left:0}
:focus-visible{outline:3px solid var(--azure);outline-offset:3px}
.take{padding-left:1.2rem}.take li{margin:.35rem 0}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
header.site{background:var(--bg);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:72px}
.brand img{height:40px;width:auto;display:block}
nav ul{display:flex;gap:28px;list-style:none;margin:0;padding:0;flex-wrap:wrap}
nav a{color:var(--ink);text-decoration:none;font-weight:600;font-size:16px;padding:6px 0;border-bottom:2px solid transparent}
nav a:hover,nav a[aria-current=page]{color:#fff;border-color:var(--purple-light)}
.eyebrow{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--olive);font-weight:700;margin:0 0 16px}
h1,h2,h3{line-height:1.08;letter-spacing:-.02em;margin:0 0 .5em;color:var(--ink)}
h1{font-size:clamp(2.4rem,6vw,4.6rem);font-weight:800}
h2{font-size:clamp(1.8rem,3.4vw,2.6rem);font-weight:800;color:var(--purple-light)}
h3{font-size:1.35rem;font-weight:700}
.hero{padding:88px 0 72px;background:radial-gradient(900px 380px at 85% -10%,rgba(97,51,126,.45),transparent 70%)}.hero p.lead{font-size:1.3rem;max-width:34em;color:var(--muted)}
.rule{width:120px;height:3px;background:var(--purple-light);margin:28px 0 0}
section{padding:64px 0}.alt{background:var(--surface);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.btn{display:inline-block;background:var(--btn);color:#fff;text-decoration:none;font-weight:700;padding:14px 26px;border-radius:6px;margin:8px 12px 8px 0;border:2px solid var(--btn)}
.btn:hover{background:var(--purple);border-color:var(--purple-light);color:#fff}
.btn.ghost{background:transparent;color:var(--azure);border-color:var(--azure)}.btn.ghost:hover{background:var(--purple);border-color:var(--purple-light);color:#fff}
.grid{display:grid;gap:24px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.card{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--purple-light);border-radius:4px;padding:24px 24px 28px;display:flex;flex-direction:column}
.alt .card{background:var(--bg)}
.card .meta{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--olive);font-weight:700;margin-bottom:10px}
.card h3 a{color:var(--ink);text-decoration:none}.card h3 a:hover{color:var(--purple-light)}
.card p{margin:.4em 0 1em;color:var(--muted);font-size:16px}.card .more{margin-top:auto;font-weight:700;font-size:16px}
.chip{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:#2c2236;color:var(--purple-light);padding:3px 10px;border-radius:99px;margin-left:8px}
.two{display:grid;gap:48px;grid-template-columns:1fr 1fr}@media(max-width:800px){.two{grid-template-columns:1fr}}
.listen{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.listen .card p{min-height:3em}
.quote{border-left:4px solid var(--purple-light);padding:8px 0 8px 24px;font-size:1.5rem;font-weight:700;line-height:1.3;max-width:28em}
.search{width:100%;max-width:520px;padding:14px 16px;border:2px solid var(--line);border-radius:6px;font:inherit;margin:8px 0 28px;background:var(--surface);color:var(--ink)}
.search::placeholder{color:#8a8398}
.search:focus{border-color:var(--azure);outline:none}
footer.site{background:var(--purple);color:#fff;padding:56px 0 40px;margin-top:0}
footer.site a{color:#fff}footer.site img{height:44px;width:auto}
footer.site ul{list-style:none;padding:0;margin:16px 0;display:flex;gap:24px;flex-wrap:wrap}
footer.site small{opacity:.9}
.crumbs{font-size:15px;margin:32px 0 0;color:var(--muted)}.crumbs a{font-weight:600}
article.ep h1{font-size:clamp(2rem,4.6vw,3.4rem)}.ep .lead{font-size:1.3rem;color:var(--muted);max-width:34em}
.facts{display:flex;gap:24px;flex-wrap:wrap;color:var(--muted);font-size:15px;margin:20px 0 28px;padding:0;list-style:none}
.facts li strong{color:var(--ink)}
@media(max-width:700px){header.site .wrap{flex-direction:column;align-items:flex-start;padding-top:12px;padding-bottom:12px}nav ul{gap:18px}.hero{padding:56px 0 48px}section{padding:48px 0}}
.note{background:var(--surface);border-left:4px solid var(--olive);padding:16px 20px;font-size:16px;color:var(--muted);margin:32px 0}
"""

def nav(prefix, current):
    items = [("Home", "index.html", "home"), ("About", "about/", "about"), ("Episodes", "episodes/", "episodes"), ("Work With Me", "work-with-me/", "work")]
    li = "".join(f'<li><a href="{prefix}{h}"{" aria-current=\"page\"" if k==current else ""}>{t}</a></li>' for t, h, k in items)
    return f'<nav aria-label="Main"><ul>{li}</ul></nav>'

def page(title, desc, path, body, prefix, current, jsonld=None, robots=None, og_type="website", image=None):
    canonical = f"{SITE}/{path}".replace("//index.html", "/")
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    im = f'<meta property="og:image" content="{image}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{image}">' if image else ""
    rb = f'<meta name="robots" content="{robots}">' if robots else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">{rb}
<link rel="canonical" href="{canonical}">
<link rel="icon" href="{prefix}assets/favicon.png"><link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="{og_type}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="{NAME}">{im}
<meta name="theme-color" content="#141118"><style>{CSS}</style>{ld}</head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap"><a class="brand" href="{prefix}index.html" aria-label="24 Hats Leadership Podcast home"><img src="{prefix}assets/logo-white.png" alt="24 Hats Leadership"></a>{nav(prefix, current)}</div></header>
<main id="main">{body}</main>
<footer class="site"><div class="wrap"><img src="{prefix}assets/logo-white.png" alt="24 Hats Leadership">
<ul><li><a href="{prefix}index.html">Home</a></li><li><a href="{prefix}about/">About</a></li><li><a href="{prefix}episodes/">Episodes</a></li><li><a href="{prefix}work-with-me/">Work With Me</a></li><li><a href="{PODCAST_PAGE}">Podcast feed</a></li><li><a href="{YOUTUBE}">YouTube</a></li></ul>
<small>Practical conversations for people-focused leadership.<br>&copy; {date.today().year} 24 Hats Leadership. All rights reserved.</small></div></footer></body></html>"""

def ep_url(r): return f"episodes/{r['slug']}/"
def listen_href(r): return r["substack"] or PODCAST_PAGE

def card(r, prefix):
    chip = '<span class="chip">Co-hosted with Chris</span>' if r["cohost"] else ""
    s = short(r["summary"], 150) if r["summary"] else ""
    p = f"<p>{esc(s)}</p>" if s else ""
    kind = "Conversation" if r["type"] == "Guest" else "Jason Kempf"
    return f'<article class="card"><div class="meta">Episode {r["ep"]} &middot; {mins(r)} min{chip}</div><h3><a href="{prefix}{ep_url(r)}">{esc(clean(r["title"]))}</a></h3>{p}<a class="more" href="{prefix}{ep_url(r)}">Read more</a></article>'

def related(r):
    pool = [x for x in eps if x["ep"] != r["ep"]]
    pool.sort(key=lambda x: (not has_body(x), abs(x["ep"] - r["ep"])))
    return pool[:3]

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "assets"))
    shutil.copy(f"{UP}/a3a05ee6-24hats-logo-black_on_white.svg", f"{OUT}/assets/logo.svg")
    shutil.copy(f"{UP}/e765a83b-image.png", f"{OUT}/assets/logo-white.png")
    shutil.copytree(os.path.join(ROOT,"thumbs","out"), f"{OUT}/assets/thumbs")
    shutil.copytree(os.path.join(ROOT,"thumbs","out_sq"), f"{OUT}/assets/thumbs-square")
    from PIL import Image
    ic = Image.open(f"{UP}/44857693-image.png").convert("RGBA")
    bbox = ic.getbbox(); ic = ic.crop(bbox)
    w, h = ic.size; s = max(w, h)
    sq = Image.new("RGBA", (s, s), (0, 0, 0, 0)); sq.paste(ic, ((s - w) // 2, (s - h) // 2))
    sq.resize((64, 64)).save(f"{OUT}/assets/favicon.png"); sq.resize((180, 180)).save(f"{OUT}/assets/apple-touch-icon.png")

    series = {"@context": "https://schema.org", "@type": "PodcastSeries", "name": NAME, "url": f"{SITE}/", "description": "Practical leadership skills and conversations with leaders building healthy teams and stronger relationships.", "author": {"@type": "Person", "name": "Jason Kempf"}, "publisher": {"@type": "Organization", "name": "24 Hats Leadership", "url": f"{SITE}/"}, "webFeed": "https://24hatsleadership.substack.com/feed"}
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "24 Hats Leadership", "url": f"{SITE}/", "founder": {"@type": "Person", "name": "Jason Kempf"}}

    # HOME
    feat = [by_ep[n] for n in (86, 70, 49)]
    home = f"""<section class="hero"><div class="wrap"><p class="eyebrow">24 Hats Leadership Podcast</p><h1>{TAG}</h1>
<p class="lead">Practical leadership skills and conversations with leaders building healthy teams and stronger relationships without burning out.</p><div class="rule"></div>
<p style="margin-top:32px"><a class="btn" href="{PODCAST_PAGE}">Listen to the podcast</a><a class="btn ghost" href="episodes/">Browse all episodes</a></p></div></section>
<section class="alt"><div class="wrap two"><div><p class="eyebrow">The show</p><h2>Leadership that keeps people at the center.</h2></div>
<div><p>Useful ideas for the everyday work of leading well. Each episode gives you something to try in an ordinary working relationship, not a theory to admire.</p>
<p>Season 1 ("Leading Is Serving") holds dozens of conversations with business owners, nonprofit leaders, and public servants from Indianapolis and the Southside. Some archive episodes are co-hosted with Chris.</p></div></div></section>
<section><div class="wrap"><p class="eyebrow">Start here</p><h2>Conversations worth carrying into Monday.</h2>
<div class="grid">{''.join(card(r, '') for r in feat)}</div><p style="margin-top:28px"><a href="episodes/"><strong>View the complete archive</strong></a></p></div></section>
<section class="alt"><div class="wrap"><p class="eyebrow">Choose your way in</p><h2>Listen wherever you like.</h2>
<div class="listen"><div class="card"><h3>Apple Podcasts</h3><p>Every episode, on your phone.</p><a class="more" href="{PODCAST_PAGE}">Listen on Apple Podcasts</a></div>
<div class="card"><h3>Spotify</h3><p>Every episode, in your queue.</p><a class="more" href="{PODCAST_PAGE}">Listen on Spotify</a></div>
<div class="card"><h3>YouTube</h3><p>Watch the conversations.</p><a class="more" href="{YOUTUBE}">Watch on YouTube</a></div></div></div></section>
<section><div class="wrap two"><div><p class="eyebrow">Work with me</p><h2>Take the conversation into your team.</h2></div>
<div><p>The ideas in this podcast are built for the moments when leadership gets real: a team under pressure, a relationship that needs repair, or a culture ready to grow.</p><p><a class="btn" href="work-with-me/">Work with me</a></p></div></div></section>"""
    write("index.html", page(f"{NAME} | 24 Hats Leadership", "Practical leadership skills and conversations with leaders building healthy teams and stronger relationships without burning out.", "", home, "", "home", [series, org]))

    # ABOUT
    about = f"""<section class="hero"><div class="wrap"><p class="eyebrow">About 24 Hats Leadership</p><h1>Jason Kempf</h1>
<p class="lead">Founder of 24 Hats Leadership and host of the {NAME}.</p><div class="rule"></div></div></section>
<section class="alt"><div class="wrap two"><div><p class="eyebrow">A note from Jason</p><h2>A practical reason to keep talking about leadership.</h2></div>
<div><p>I make this podcast because leadership gets talked about in ways that can feel far removed from an actual Tuesday at work.</p>
<p>Most of us are trying to build healthy teams, have stronger relationships, and do good work without burning ourselves out in the process.</p>
<p>So I bring useful leadership skills to the conversation, along with honest stories about what those skills look like when things are complicated, personal, or simply unfinished.</p>
<p>My hope is that each episode gives you something you can try in an ordinary relationship. Leadership is practiced there, not performed from a stage.</p></div></div></section>
<section><div class="wrap"><p class="quote">Leadership is practiced in ordinary relationships, not performed from a stage.</p></div></section>
<section class="alt"><div class="wrap two"><div><p class="eyebrow">The wider work</p><h2>The podcast is one way into the work.</h2></div>
<div><p>The ideas on the podcast also inform my work with leaders and teams: how we listen, how we handle tension, and how we keep showing up when leadership gets difficult.</p>
<p>That thinking comes from real conversations and ordinary working relationships. The aim is practical and human: to help people build healthier teams without burning themselves out.</p>
<h3>Leadership conversations</h3><p>Making room for clearer decisions, useful challenge, and the conversations people tend to avoid.</p>
<h3>Healthier team relationships</h3><p>Practicing trust, boundaries, and repair in the everyday moments that shape how a team works.</p>
<p>Hear the ideas in practice through the <a href="../episodes/">episodes</a>, or <a href="../work-with-me/">work with me directly</a>.</p></div></div></section>"""
    person = {"@context": "https://schema.org", "@type": "Person", "name": "Jason Kempf", "jobTitle": "Founder", "worksFor": {"@type": "Organization", "name": "24 Hats Leadership"}, "url": f"{SITE}/about/"}
    write("about/index.html", page("About Jason Kempf | 24 Hats Leadership Podcast", "Jason Kempf is the founder of 24 Hats Leadership and host of the 24 Hats Leadership Podcast, on practical, people-focused leadership.", "about/", about, "../", "about", [person]))

    # WORK WITH ME
    work = f"""<section class="hero"><div class="wrap"><p class="eyebrow">Work with 24 Hats Leadership</p><h1>Let's make leadership more workable.</h1>
<p class="lead">If you're leading a team, strengthening relationships, or navigating a difficult leadership situation, we can make space to understand what's happening and find a useful way forward.</p>
<p><a class="btn" href="{CONTACT}">Book a conversation</a></p></div></section>
<section class="alt"><div class="wrap"><p class="eyebrow">Ways to work together</p><h2>Two ways to move forward.</h2>
<div class="two"><div><h3>Training: shared learning for your whole team.</h3><p>Build practical leadership habits together, strengthen communication and relationships, and give your people a common language for working well.</p><p>Notice what is happening sooner. Have clearer, more useful conversations. Practice habits the team can use together.</p></div>
<div><h3>Consulting: focused support for one challenge.</h3><p>Work through a difficult conversation, team dynamic, or leadership decision with space to slow down, see the options, and choose a workable next step.</p><p>Make sense of the situation. Prepare for a conversation that matters. Choose a clear next step.</p></div></div></div></section>
<section id="contact"><div class="wrap two"><div><p class="eyebrow">A place to begin</p><h2>Bring the situation you're thinking about.</h2></div>
<div><p>You do not need to have the right words or a finished plan. Start with what is happening, what feels difficult, and what you would like to understand better.</p>
<p>Leading a team through change. Improving trust or communication. Working through conflict. Deciding what support would actually help.</p>
<p>The first conversation is simply a chance to talk through what your people need and decide whether I can help. No pressure, just a conversation.</p>
<p><a class="btn" href="{CONTACT}">Book a conversation</a></p></div></div></section>"""
    write("work-with-me/index.html", page("Work With Me | 24 Hats Leadership Podcast", "Leadership training for your whole team or focused consulting on one challenge, with Jason Kempf of 24 Hats Leadership. Start with a conversation.", "work-with-me/", work, "../", "work", [org]))

    # EPISODES INDEX
    cards = "".join(card(r, "../") for r in eps)
    epi = f"""<section class="hero" style="padding-bottom:24px"><div class="wrap"><p class="eyebrow">Season 1 archive</p><h1>Leading Is Serving: the archive.</h1>
<p class="lead">Dozens of conversations with business owners, nonprofit leaders, and public servants from Indianapolis and the Southside. Some episodes are co-hosted with Chris. Start anywhere.</p>
<label for="q" class="eyebrow" style="margin-top:28px;display:block">Search episodes</label><input id="q" class="search" type="search" placeholder="Try &quot;burnout&quot;, &quot;trust&quot;, or a guest name"></div></section>
<section style="padding-top:8px"><div class="wrap"><div class="grid" id="list">{cards}</div><p id="none" hidden>No episodes match that search.</p></div></section>
<script>(function(){{var q=document.getElementById('q'),cs=[].slice.call(document.querySelectorAll('#list .card')),n=document.getElementById('none');q.addEventListener('input',function(){{var v=q.value.toLowerCase(),c=0;cs.forEach(function(x){{var m=x.textContent.toLowerCase().indexOf(v)>-1;x.style.display=m?'':'none';if(m)c++}});n.hidden=c>0}})}})();</script>"""
    il = {"@context": "https://schema.org", "@type": "ItemList", "name": "Season 1: Leading Is Serving (archive)", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{ep_url(r)}", "name": clean(r["title"])} for i, r in enumerate(eps)]}
    write("episodes/index.html", page("Episodes: the Leading Is Serving archive | 24 Hats Leadership Podcast", "Browse Season 1 of the 24 Hats Leadership Podcast: conversations with business owners, nonprofit leaders, and public servants from Indianapolis.", "episodes/", epi, "../", "episodes", [il]))

    # EPISODE PAGES
    sitemap = [("", "1.0"), ("about/", "0.7"), ("episodes/", "0.9"), ("work-with-me/", "0.8")]
    for r in eps:
        t = clean(r["title"])
        mt = f"{t} | {NAME}"
        if len(mt) > 70: mt = t
        desc = short(r["summary"], 155) if r["summary"] else f"Episode {r['ep']} of the {NAME}: {t}."
        d = date.fromisoformat(r["date"]).strftime("%B %-d, %Y")
        who = "Jason Kempf and Chris" if r["cohost"] else "Jason Kempf"
        tk = r.get("takeaways") or []
        take = ('<h2>What you will take away</h2><ul class="take">' + "".join(f"<li>{esc(clean(x))}</li>" for x in tk) + "</ul>") if tk else ""
        lead = f'<p class="lead">{esc(clean(r["summary"]))}</p>' if r["summary"] else ""
        rel = "".join(card(x, "../../") for x in related(r))
        body = f"""<div class="wrap"><p class="crumbs"><a href="../../index.html">Home</a> / <a href="../">Episodes</a> / Episode {r['ep']}</p></div>
<section style="padding-top:24px"><div class="wrap"><article class="ep"><p class="eyebrow">Episode {r['ep']}{' &middot; Co-hosted with Chris' if r['cohost'] else ''}</p><h1>{esc(t)}</h1>{lead}
<ul class="facts"><li><strong>Published</strong> {d}</li><li><strong>Length</strong> {mins(r)} minutes</li><li><strong>Host</strong> {who}</li></ul>
{take}<p><a class="btn" href="{listen_href(r)}">Listen to this episode</a><a class="btn ghost" href="{PODCAST_PAGE}">Subscribe to the podcast</a></p></article></div></section>
<section class="alt"><div class="wrap"><p class="eyebrow">Keep listening</p><h2>More episodes.</h2><div class="grid">{rel}</div></div></section>
<section><div class="wrap two"><div><h2>Take it into your team.</h2></div><div><p>If this conversation hit close to home, we can talk through what it looks like in your team.</p><p><a class="btn" href="../../work-with-me/">Work with me</a></p></div></div></section>"""
        iso = f"PT{r['minutes']}M"
        ld = {"@context": "https://schema.org", "@type": "PodcastEpisode", "name": t, "url": f"{SITE}/{ep_url(r)}", "datePublished": r["date"], "timeRequired": iso, "episodeNumber": r["ep"], "partOfSeries": {"@type": "PodcastSeries", "name": NAME, "url": f"{SITE}/episodes/"}, "author": {"@type": "Person", "name": "Jason Kempf", "url": f"{SITE}/about/"}, "inLanguage": "en-US"}
        if r["summary"]: ld["description"] = clean(r["summary"])
        if r["substack"]: ld["associatedMedia"] = {"@type": "AudioObject", "contentUrl": r["substack"]}
        indexable = has_body(r)
        write(f"episodes/{r['slug']}/index.html", page(mt, desc, ep_url(r), body, "../../", "episodes", [ld], robots=None if indexable else "noindex,follow", og_type="article", image=f"{SITE}/assets/thumbs/ep{r['ep']:02d}.jpg"))
        if indexable: sitemap.append((ep_url(r), "0.6"))

    today = date.today().isoformat()
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>" for p, pr in sitemap) + "</urlset>")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    write("404.html", page("Page not found | 24 Hats Leadership Podcast", "That page could not be found.", "404.html", '<section class="hero"><div class="wrap"><h1>That page moved.</h1><p class="lead">Try the <a href="/">home page</a> or the <a href="/episodes/">episode archive</a>.</p></div></section>', "/", "", robots="noindex"))
    write(".nojekyll", "")
    print("pages:", len(eps) + 4, "indexable episodes:", len(sitemap) - 4)

build()
