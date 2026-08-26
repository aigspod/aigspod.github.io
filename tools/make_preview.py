#!/usr/bin/env python3
"""Turn mood/index.html or mill/index.html into a self-contained page for an Artifact.

Artifacts run under a strict CSP: no same-origin fetch of feed.xml, no ../images,
no archive.org audio. So we parse the feed here and inline it as window.AIGS_EPISODES
(the page prefers that over fetching), swap thumbnails for data URIs, and replace
the <audio> players with a note. Google Fonts still load.

  python3 tools/make_preview.py <thumbdir> <out.html> [page]   # page: fun | mill
"""
import sys, re, json, base64, pathlib, html, email.utils
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
NS = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
thumbdir, out = pathlib.Path(sys.argv[1]), sys.argv[2]
which = sys.argv[3] if len(sys.argv) > 3 else 'mood'


def episodes():
    items = []
    for it in ET.parse(ROOT / 'feed.xml').getroot().find('channel').findall('item'):
        n = int(it.findtext('itunes:episode', namespaces=NS) or 0)
        if not n:
            continue
        dur = (it.findtext('itunes:duration', namespaces=NS) or '').strip()
        dt = email.utils.parsedate_to_datetime(it.findtext('pubDate'))
        secs = 0
        for part in (dur.split(':') if dur else []):
            secs = secs * 60 + int(part)
        img = 'images/ep%03d.png' % n
        desc = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', html.unescape(it.findtext('description') or ''))).strip()
        items.append({
            'n': n, 'title': (it.findtext('title') or '').strip(), 'dur': dur, 'secs': secs,
            'dateLabel': dt.strftime('%b %-d, %Y'),
            'img': img, 'thumb': img.replace('images/', 'images/thumbs/').replace('.png', '.jpg'),
            'audio': it.find('enclosure').get('url'),
            'desc': desc,
        })
    return sorted(items, key=lambda e: -e['n'])


eps = episodes()
page_html = (ROOT / which / 'index.html').read_text()

uris = {p.stem: 'data:image/jpeg;base64,' + base64.b64encode(p.read_bytes()).decode()
        for p in sorted(thumbdir.glob('ep*.jpg'))}

# the show cover is referenced by path, not through the episode list
cover = ROOT / 'images' / 'thumbs' / 'funcover.jpg'
cover_uri = ('data:image/jpeg;base64,' + base64.b64encode(cover.read_bytes()).decode()
             if cover.exists() else '')
table = ',\n'.join('%d:"%s"' % (int(k[2:]), v) for k, v in sorted(uris.items()))

# inline data + point every image at the embedded thumbnail
page_html = page_html.replace('<script>\n', '<script>\nconst THUMBS={%s};\nwindow.AIGS_EPISODES=%s;\n'
                    % (table, json.dumps(eps)), 1)
page_html = page_html.replace('../${e.thumb}', '${THUMBS[e.n]||""}')
page_html = page_html.replace('data-full="../${e.img}"', '')
page_html = page_html.replace('src="../images/thumbs/funcover.jpg"', 'src="%s"' % cover_uri)
page_html = page_html.replace('data-full="../images/funcover.png"', '')
page_html = re.sub(r'<link rel="(?:apple-touch-)?icon"[^>]*>', '', page_html)

# audio can't stream from archive.org under the artifact CSP — say so instead
page_html = re.sub(r'<audio[^>]*></audio>',
              '<div class="preview-note">▶ audio plays on the real site</div>', page_html)
# links out of the artifact sandbox have nowhere to go
page_html = page_html.replace('<a href="../">← BACK TO THE NORMAL VERSION</a> · ', '')
page_html = page_html.replace('<a href="../">← the normal version</a> ·', '')
page_html = page_html.replace('<a href="../mood/">severe weather mode ⚡</a> ·', '')

# strip the document skeleton — Artifact supplies <!doctype>/<head>/<body>
page_html = re.sub(r'^.*?<head>', '', page_html, flags=re.S)
page_html = page_html.replace('</head>', '').replace('</html>', '')
page_html = re.sub(r'<body[^>]*>', '', page_html).replace('</body>', '')
page_html = page_html.replace('<title>AIGS POD // CHAOS LAB</title>', '<title>Chaos Lab</title>', 1)
page_html = page_html.replace('<title>The Paper Mill — The AIGS Pod</title>',
                              '<title>The Paper Mill</title>', 1)

page_html += """
<div class="pv-banner">PROTOTYPE PREVIEW · low-res covers, audio disabled — both are live on the real site</div>
<style>
.preview-note{font:600 11px/1 ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase;
  opacity:.55;padding:.55rem .8rem;border:1px dashed currentColor;border-radius:6px;
  display:inline-block;margin:1rem 1.2rem}
.pv-banner{position:fixed;bottom:0;left:0;right:0;z-index:8;background:#171029;color:#c9bfe0;
  border-top:1px solid #2a2040;font-family:'Space Mono',ui-monospace,monospace;font-size:10px;
  letter-spacing:.1em;text-align:center;padding:.45rem .8rem;text-transform:uppercase}
</style>
"""
pathlib.Path(out).write_text(page_html)
print(out, '%.1f MB' % (pathlib.Path(out).stat().st_size / 1e6), '·', len(eps), 'episodes ·', which)
