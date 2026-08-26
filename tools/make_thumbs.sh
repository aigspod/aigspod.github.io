#!/bin/sh
# Regenerate web-sized episode thumbnails (640px JPEG) from the full-res artwork.
# Full-res images/epNNN.png stay authoritative for the RSS feed / Apple Podcasts;
# images/funcover.png is the /fun page's artwork; kept at 1400x1400 too so it can be
# promoted to the real podcast cover without re-exporting.
# these thumbs are what the website loads (49MB -> ~3MB).
set -e
cd "$(dirname "$0")/.."
mkdir -p images/thumbs
for f in images/ep*.png images/cover.png images/funcover.png; do
  b=$(basename "$f" .png)
  sips -s format jpeg -s formatOptions 78 -Z 640 "$f" --out "images/thumbs/$b.jpg" >/dev/null
  echo "  images/thumbs/$b.jpg"
done
