---
title: "A Faster Gelato"
author: "Edmund Goodman"
date: 2024-10-27T23:51:22Z
---

I love Jack's Gelato. Unfortunately, their website's menu sucks.
[So I fixed it.](https://edmundgoodman.co.uk/gelato/)

<!--more-->

## Why the existing menu sucks

The most noticeable issue of the current website is that it takes **4.5 seconds**
to display the menu. To add insult to injury, the text
"Can take a few seconds to Load.. \[sic\]" is shown whilst you wait.

{{< figure
    src="/images/posts/a_faster_gelato/offending_text.png"
    alt="A screenshot of Jack's Gelato menu website."
    caption="A screenshot of Jack's Gelato menu website.">}}

Using Firefox's web inspector tools, we can trace the network requests made to
load the website HTML to attempt to diagnose the sluggish loading times.

{{< figure
    src="/images/posts/a_faster_gelato/jacks_gelato_slow_load.png"
    alt="A screenshot of the Firefox network inspector for the page load."
    caption="A screenshot of the Firefox network inspector for the page load.">}}

This shows that the dominant factor in menu latency is that it is served as an
embedded Google Doc through a Wix plugin. This plugin spends over a second
interacting with its [developer's website](https://www.mymobileapp.online), then
201ms retrieving a placeholder document to show before it starts retrieving the
actual menu document. After this, it finally retrieves the menu document for a
total of 4.5 seconds menu latency.

{{< figure
    src="/images/posts/a_faster_gelato/wix_placeholder.png"
    alt="A screenshot of the placeholder document, retrieved by blocking requestt."
    caption="A screenshot of the placeholder document, retrieved by blocking request.">}} 

On top of the egregiously slow load times, the website transmits 9.5MB zipped of
resources. In contrast, the gzipped text content of a
[representative menu](https://raw.githubusercontent.com/EdmundGoodman/jacks-menu-history/refs/heads/main/raw/24_10_04__benet_street.txt) is 570 bytes [^1]. On my
pay-as-you-go data plan charging 10p per MB [^2], it costs nearly one pound to
load the menu website. Whilst much of this blame can be attributed
to price gouging by mobile service providers, it does strongly motivate making
a lighter and faster website.

## How I made it better

Tl;dr (full write-up coming soon):

1. Wrote a [Python package](https://pypi.org/project/jacks-menu/) which:
   - Extracts the menu Google Doc URL using Selenium
   - Retrieves a text representation of the menu using the Google Docs API
   - Parses the text representation with a finite-state machine [^3]
   - Generates a markdown document from the parsed menu
2. Wrote a [cron job](https://github.com/EdmundGoodman/jacks-menu-history/blob/main/.github/workflows/gelato.yml) in GitHub Actions which runs the package at 10:20am every
   day to retrieve the menu into an [artefact repository](https://github.com/EdmundGoodman/jacks-menu-history)
3. Wrote [another cron job](https://github.com/EdmundGoodman/edmundgoodman.github.io/blob/main/.github/workflows/gh-pages.yml) which deploys the generated markdown menu
   artefacts onto my statically hosted website on GitHub Pages (for free) at
   10:25am every day

My version of the website takes 147ms to load (3% of the original time), and
transmits only 9.52kB of data (0.8% of the original size, 0.7p cost in
pay-as-you-go data). By omitting the favicon, inlining the CSS, and eliding
the inlined SVG icons this could likely be reduced to ~2kB and 40ms -- but for
now I am happy with the performance.

{{< figure
    src="/images/posts/a_faster_gelato/mine_trace.png"
    alt="A screenshot of the Firefox network inspector for the page load."
    caption="A screenshot of the Firefox network inspector for the page load.">}}

## Please don't sue me disclaimer

All copyright and intellectual property of the menu contents belongs to
[Jack's Gelato](https://www.jacksgelato.com/).

I will comply with any requests to take this website down, but I hope it never
comes to that. For me, this is just a fun different way to access the menu,
as it makes it a bit easier/faster to work out what the flavours are each day.

Additionally, their website runs no advertising so this is not depriving them of
profit in that respect.


[^1]: This means the information a customer cares about, which icecream
is available that day, is transmitted at approximately 890 bits per second,
0.00356% of the [lower-bound average 4G bandwidth in the UK](https://simrush.com/fastest-4g-network-uk/).
[^2]: [Three Pay As You Go Price Guide](https://www.three.co.uk/content/dam/threedigital/terms-and-conditions/price-guides/latest-price-guides/paygplans-priceguide-12052023.pdf)
[^3]: This by identity could be expressed as a regular expression, but the
finite-state machine is a little more readable and hence maintainable when
the menu format inevitably changes
