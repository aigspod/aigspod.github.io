#!/bin/sh
# Regenerate images/mill-og.png (the 1200x630 link-preview card for /mill/).
#
# The card lives at tools/og/mill-og.html and reuses the mill's own SVG and drawing
# code, so it stays in step with the page. It is not fully automatic: serve the repo,
# open the card in a browser at a viewport of at least 1200x630, screenshot it, and
# crop the top-left 1200x630. The crop step is the only fiddly part:
#
#   python3 -m http.server 8899
#   open http://localhost:8899/tools/og/mill-og.html
#   # screenshot to /tmp/shot.png, then:
#   swift tools/og/crop.swift /tmp/shot.png images/mill-og.png 0 0 1200 630
#
# Verify afterwards:
#   sips -g pixelWidth -g pixelHeight images/mill-og.png   # must be 1200x630
echo "See the comments in this file — regenerating the card needs a browser screenshot."
