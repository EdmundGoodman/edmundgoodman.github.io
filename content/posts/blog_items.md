---
title: "Blog Items"
author: "Edmund Goodman"
date: 2023-01-08T14:12:29Z
draft: false
---

## Blog items

This is a test of all the items which can be embedded in a blog post. If I broke
something in the server side rendering it will be messed up here, like a canary
in a mine.

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

### Centered images

{{< centered_image
    src="/images/france_photo_squared.jpg"
    alt="A photo of me sitting on a pillar in Paris."
    caption="A photo of me sitting on a pillar in Paris." >}}
