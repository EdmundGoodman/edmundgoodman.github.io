---
title: "Using Git Bisect"
author: "Edmund Goodman"
date: 2025-04-08T20:39:49+01:00
draft: True
---

Have you ever wanted to find bugs in your code? Like *really* fast? If so, do I
have the `git` command for you...

<!--more-->

## Motivation

## How it works

## Using `git bisect`

You might be thinking "this is cool, but will I ever actually use this"?

If you are developing small personal projects and have a full understanding of
the entire codebase's context, it is probably slower to set up and use `git
bisect`. However, for large open source codebases with many commits made by
people other than you, it is incredibly useful. Below, I discuss a real-world
example where I used `git bisect` to diagnose and fix
[a bug in xDSL](https://github.com/xdslproject/xdsl/issues/4203), an open-source
compiler framework I worked on as part of my Master's thesis [^2].

### The bug

### Setting up the bisection

```bash
git bisect start
```

Then, you pick a commit in which the bug occurs. This is normally the current
`HEAD`, in which case you run:

```bash
git bisect bad
```

Next, you pick a past commit in which the bug does not occur. It is often
easiest to pick the first commit made in the repository, which in xDSL's case is
`43192bdd8`.

```bash
git bisect good 43192bdd8
```

Since the bisection uses a binary search, the time taken scales logarithmically
with the number of commits, so picking a large commit range does not incur a
significant cost. However, if the bug is removed and re-introduced multiple
times, you must pick a window after the previous removal of the bug to guarantee
correct results!

### Running the bisection

```
git bisect run python3 -c "import xdsl.dialects.arith"
```

Finally, you can finish the bisection with:

```bash
git bisect reset
```

## Summary

## References

[^1]: <https://git-scm.com/docs/git-bisect>
[^2]: <https://github.com/xdslproject/xdsl>
