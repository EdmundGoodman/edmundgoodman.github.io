---
title: "Using Google Search Console for my blog"
author: "Edmund Goodman"
date: 2025-06-22T20:59:25+01:00
draft: true
---

Short summary of/introduction to the post

<!--more-->

## Verifying with Google Search Console

First, navigate to <https://search.google.com/search-console/welcome>. This page
will then prompt you to either verify domain or page ownership. 

### Setting the record on NameCheap

I use NameCheap as my domain-name registrar for <https://edmundgoodman.co.uk/>.
The value provided for verification can be set in the Host Records section of
the Advanced DNS pane for your domain. The new record should look similar to the
following, with the Host value "@" referring to you domain.

| **Type** | **Host** | **Value**    | **TTL**   |
|----------|----------|--------------|-----------|
| TXT      | @        | COPIED_VALUE | Automatic |

### Checking the record has been updated

Once the record has been set in the UI, it takes a few minutes to propagate and
become visible. In order to check if this has happened, we can use the `dig`
command:

```bash
dig edmundgoodman.co.uk TXT +short | grep google-site-verification
```

Once this command returns the record, you can press the verify button in the
Google Search Console verification pane, and the domain property should be
added.

## Search engine optimisation with Google Search Console

Some resources:

- https://djangocas.dev/blog/hugo/tips-on-hugo-seo/
- https://www.webpagetest.org/
- https://storychief.io/blog/indexing
- https://travellemming.com/perspectives/ftc-letter-google-censors-indie-publishers-with-ai/
- https://support.google.com/webmasters/thread/243420770/why-is-my-blog-pages-not-indexed?hl=en
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://support.google.com/webmasters/answer/10267942
