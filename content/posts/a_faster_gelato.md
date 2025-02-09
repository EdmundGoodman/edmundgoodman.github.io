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

Using FireFox's web inspector tools, we can trace the network requests made to
load the website to attempt to diagnose the sluggish loading times.

{{< figure
    src="/images/posts/a_faster_gelato/jacks_gelato_slow_load.png"
    alt="A screenshot of the FireFox network inspector for the page load."
    caption="A screenshot of the FireFox network inspector for the page load.">}}

This shows that the dominant factor in menu latency is that it is served as an
embedded Google Doc through a Wix plugin. This plugin spends 201ms retrieving a
placeholder document to show before it starts retrieving the actual menu
document. After this, it retrieves the menu twice sequentially before rendering
it to the DOM, for a total of 4.5 seconds.

{{< figure
    src="/images/posts/a_faster_gelato/wix_placeholder.png"
    alt="A screenshot of the placeholder document, retrieved by blocking requestt."
    caption="A screenshot of the placeholder document, retrieved by blocking request.">}} 

On top of the egregiously slow load times, the website transmits 9.5MB zipped of
resources. In contrast, the gzipped text content of a
[representative menu](https://raw.githubusercontent.com/EdmundGoodman/jacks-menu-history/refs/heads/main/raw/24_10_04__benet_street.txt) is 570 bytes [^1]. On my
pay-as-you-go data plan charging 10p per MB [^2], it costs nearly one pound to
load the menu website. Whilst much of this blame can be attributed
to price-gouging by mobile service providers, it does strongly motivate making
a lighter and faster website.


## How I made it better

Coming soon...

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
