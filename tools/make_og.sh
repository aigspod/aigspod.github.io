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
#
# /live/ has its own card, tools/og/live-og.html -> images/live-og.png, which lifts the
# study drawing out of live/index.html. Headless Chrome renders it exactly, no crop needed:
#
#   python3 -m http.server 8765
#   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
#     --hide-scrollbars --force-device-scale-factor=1 --window-size=1200,630 \
#     --virtual-time-budget=6000 --screenshot=images/live-og.png \
#     http://localhost:8765/tools/og/live-og.html
# /mull/ works the same way: tools/og/mull-og.html -> images/mull-og.png, lifting the desk drawing
# out of mull/index.html. Same headless command, pointed at tools/og/mull-og.html.
#
# The show cover and the front page's card are set over the text-free painting, images/cover-art.png:
#   tools/og/cover.html    -> images/cover.png     (--window-size=1400,1400; then bump ?v= on cover.png in feed.xml)
#   tools/og/home-og.html  -> images/home-og.png   (--window-size=1200,630)
#   tools/og/yt-banner.html -> the YouTube channel banner, not kept in the repo (--window-size=2560,1440; ?guides shows the crops)
# Chrome isn't always installed; Microsoft Edge takes the same flags.
echo "See the comments in this file — regenerating the card needs a browser screenshot."
