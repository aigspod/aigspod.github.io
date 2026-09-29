#!/usr/bin/env python3
"""Refresh the feed snapshot inside mull/index.html.

/mull/ reads feed.xml at runtime, but a page opened straight from disk (file://) can't
fetch it, so it falls back to a small snapshot of the feed kept at the bottom of the page:
each episode's number, title, date and the paper link from its description. Run this
after adding an episode so the file:// view stays in step with the served one.

  python3 tools/mull_snapshot.py
"""
import re, json, pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
NS = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
LINK = re.compile(r'(?:Paper|Preprint|Link):\s*(https?://\S+)')

eps = []
for it in ET.parse(ROOT / 'feed.xml').getroot().find('channel').findall('item'):
    n = int(it.findtext('itunes:episode', namespaces=NS) or 0)
    if not n:
        continue
    links = [re.sub(r'[.,;)]+$', '', m) for m in LINK.findall(it.findtext('description') or '')]
    eps.append({'n': n, 'title': (it.findtext('title') or '').strip(),
                'date': (it.findtext('pubDate') or '').strip(), 'link': links[-1] if links else ''})
eps.sort(key=lambda e: e['n'])

page = ROOT / 'mull' / 'index.html'
html = page.read_text()
snap = json.dumps(eps, ensure_ascii=False, indent=0).replace('</', '<\\/')
new, k = re.subn(r'(<script type="application/json" id="feed-snapshot">).*?(</script>)',
                 lambda m: m.group(1) + snap + m.group(2), html, flags=re.S)
assert k == 1, 'feed-snapshot block not found in mull/index.html'
page.write_text(new)
print(f'mull/index.html: snapshot of {len(eps)} episodes')
