---
title: "Parallelism in Egg"
author: "Edmund Goodman"
date: 2025-08-07T11:43:19+01:00
---

{{< note title="A note on provenance" >}}
I performed the work described in this blog post as my mini-project for the
[R244 Large-Scale Data Processing and Optimisation](https://www.cl.cam.ac.uk/~ey204/teaching/ACS/R244_2024_2025/index.html)
reading group during my MPhil.

I'd like to thank [Dr Eiko Yoneki](https://www.cl.cam.ac.uk/~ey204/) for leading
the reading group, which introduced me to a wide variety of interesting topics
including e-graphs for compiler rewrites discussed below.
{{< /note >}}

The core of the egg ("e-graphs good") project is a library providing a flexible
and performant implementation of the equality graph (e-graph) data structure,
providing a re-usable basis for leveraging equality saturation in program
optimisers to address the phase-ordering problem of compilers. This mini-project
explores the performance characteristics of the egg library through benchmarking
and profiling techniques, and uses this information to guide the design and
assess the suitability of data parallelism for its applications. We conclude
that Rust's rich support for multithreading allows data parallelism to be
leveraged in egg, but many portions of the algorithm rely on shared mutable
state, so the approach can only provide incremental performance gains as a
corollary of Amdahl's law.

<!--more-->

## Full report

{{< iframe url="/files/posts/parallelism_in_egg/R244_edjg2_project.pdf" >}}
