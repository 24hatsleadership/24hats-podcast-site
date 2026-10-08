"""Weekly check: add any new Substack podcast episodes to src/data/episodes_pages.json.
Prints the number of episodes added. New pages are noindex until a human reviews the PR."""
import json, re, sys, html, urllib.request
import xml.etree.ElementTree as ET
FEED = "https://24hatsleadership.substack.com/feed"
DATA = "src/data/episodes_pages.json"
NS = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd", "content": "http://purl.org/rss/1.0/modules/content/"}

def slugify(t):
    s = re.sub(r"[^a-z0-9]+", "-", t.lower().replace("'", "")).strip("-")
    return s[:70].rstrip("-")

def strip(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h or ""))).strip()

def main():
    req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (podcast-site-check)"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
    data = json.load(open(DATA))
    known = {r["substack"] for r in data if r.get("substack")}
    added = 0
    items = list(root.iter("item"))
    for it in reversed(items):  # oldest first
        link = (it.findtext("link") or "").strip()
        if not link or link in known:
            continue
        title = strip(it.findtext("title"))
        desc = strip(it.findtext("description")) or strip(it.findtext("content:encoded", namespaces=NS))
        desc = desc.replace("—", ",")
        if len(desc) > 300: desc = desc[:300].rsplit(" ", 1)[0].rstrip(",;:") + "..."
        dur = (it.findtext("itunes:duration", namespaces=NS) or "0").strip()
        secs = sum(int(p) * m for p, m in zip(reversed(dur.split(":")), (1, 60, 3600))) if dur.replace(":", "").isdigit() else 0
        from email.utils import parsedate_to_datetime
        d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        ep = max(r["ep"] for r in data) + 1
        slug = slugify(title)
        mins = max(1, round(secs / 60))
        rec = {"ep": ep, "date": d, "minutes": mins, "type": "Hosts", "action": "Keep", "rating": "New",
               "title": title, "original": title, "slug": slug, "path": f"/episodes/{slug}",
               "meta_title": f"{title} | 24 Hats Leadership"[:75], "summary": desc, "substack": link, "cohost": False,
               "jsonld": json.dumps({"@context": "https://schema.org", "@type": "PodcastEpisode", "name": title,
                 "url": "{SITE}/episodes/" + slug, "datePublished": d, "timeRequired": f"PT{secs//60}M{secs%60}S",
                 "episodeNumber": ep, "partOfSeries": {"@type": "PodcastSeries", "name": "24 Hats Leadership Podcast", "url": "{SITE}/episodes"},
                 "author": {"@type": "Person", "name": "Jason Kempf", "url": "{SITE}/about"},
                 "associatedMedia": {"@type": "AudioObject", "contentUrl": link}})}
        data.append(rec); known.add(link); added += 1
    if added:
        json.dump(data, open(DATA, "w"), indent=1, ensure_ascii=False)
    print(added)

if __name__ == "__main__":
    main()
