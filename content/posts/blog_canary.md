---
title: "Blog Canary"
author: "Edmund Goodman"
date: 2023-01-08T14:12:29Z
draft: false
---

In 1895, John Scott Haldane proposed bringing warm-blooded animals, most
commonly canaries, into mines to detect high levels of carbon monoxide. This
worked because they would become sick (and stop singing) before the miners did.
Because of this, "Canary in a coal mine" is commonly used as an idiom for
something which warns people of danger.

This blog post is (in a very convoluted sense) a canary for my website, as it
exercises the elements which can be embedded in a blog post. If I broke
something in the server side rendering it will be messed up here, like a canary
in a coal mine.

<!--more-->

### Inline code

```python
def inc(x: int) -> int:
    return x + 1

print("This is a test of rendering code inside markdown. Long lines should wrap around!")
assert inc(0) == 1

```

### Line breaks

This is some text.

{{< br >}}

This is some more text, after a line break.

### Figures

{{< figure
    src="/images/france_photo_squared.jpg"
    alt="A photo of me sitting on a pillar in Paris."
    caption="A photo of me sitting on a pillar in Paris." >}}

### Internal references

[Hello there post]({{< ref "posts/hello_there.md" >}})

### Footnotes

This sentence has a footnote {{< footnote "1" "This is a footnote" >}}.

### Inline HTML

{{< raw_html >}}

<p style="font-family: kanzlei;  font-size: 32px;">Content in a decorative font</p>
{{< /raw_html >}}

### Admonitions

{{< note >}}
This is a note admonition.
{{< /note >}}

{{< warning title="Custom warning title" >}}
This is a note admonition using a custom `title`.
{{< /warning >}}

{{< error >}}
This is an error admonition.
{{< /error >}}

### References

{{< footnote_list >}}
