---
title: "Blog Canary"
author: "Edmund Goodman"
date: 2023-01-08T14:12:29Z
draft: false
---

In 1895, John Scott Haldane proposed bringing warm-blooded animals, most
commonly canaries, into mines to detect high levels of carbon monoxide [^1].
This worked because they would become sick (and stop singing) before the miners did.
Because of this, "Canary in a coal mine" is commonly used as an idiom for
something which warns people of danger.

This blog post is (in a very convoluted sense) a canary for my website, as it
exercises the elements which can be embedded in a blog post. If I broke
something in the server side rendering it will be messed up here, like a canary
in a coal mine.

<!--more-->

## Inline code

```python
def inc(x: int) -> int:
    return x + 1

print("This is a test of rendering code inside markdown. Long lines should wrap around!")
assert inc(0) == 1

```

## Line breaks

This is some text.

{{< br >}}

This is some more text, after a line break.

## Figures

{{< figure
    src="https://picsum.photos/800/600"
    alt="A randomly generated photo from Lorem Picsum"
    caption="A randomly generated photo from [Lorem Picsum](https://picsum.photos/)." >}}

## Internal references

[Hello there post]({{< ref "posts/hello_there.md" >}})

## Inline HTML

{{< raw_html >}}
<span style="color: red;">This is some text styled through raw HTML.</span>
{{< /raw_html >}}

## Block comment

> The chief aim of the present investigation has been to determine
> experimentally the causes of the symptoms produced in man by carbonic oxide,
> and particularly the relation of the changes in the blood to the symptoms, to
> the percentage of carbonic oxide breathed, and to the period during which the
> inhalation is continued.
>
> -- *John Scott Haldane*

## Admonitions

{{< note >}}
This is a note admonition.

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
{{< /note >}}

{{< warning title="Custom warning title" >}}
This is a note admonition using a custom `title`.
{{< /warning >}}

{{< error >}}
This is an error admonition.
{{< /error >}}

## References

[^1]: Haldane J. The Action of Carbonic Oxide on Man. The Journal of Physiology. 1895 Nov 16; 18(5-6):430-62.
