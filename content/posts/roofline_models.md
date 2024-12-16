---
title: "Roofline Models"
author: "Edmund Goodman"
date: 2024-09-10T20:03:27+01:00
draft: true
---

Roofline models are
This blog post explains and provides an intuition for roofline models, and shows how
they can be used in the real world to inform hand-crafted performance
optimisations of high-level code.

<!--more-->

## A *very* simple model of computation

### Abstractions for hardware

### Abstractions for software

<!-- -->

## Bounds on performance

### Peak floating point performance

### Peak memory bandwidth

### Bringing it together

Performance can be bottlenecked by either the peak floating point performance
or the peak memory bandwidth. Hence, we can approximate total performance as:

$$
P_{max} = min(P_{peak}, I_c \time B_{peak})
$$

Then, when we plot this on a graph, we see the shape of our roofline plot:

<!-- -->

## Measuring properties

### Hardware information

### Hand counting

### Perf

### Likwid

<!-- -->

## Drawing rooflines

### Empirical roofline toolkit

### Intel Advisor

<!-- -->

## Informing optimisations

### Applying rooflines to software

To characterise the performance of a piece of code, we can measure its
arithmetic intensity and floating point throughput, then plot it on the roofline
for the hardware on which it is running. An example of this plot is shown
below in Figure .

<!-- Roofline plot of optimal, and two types of limited - coloured quadrants -->

Explanation of what/why is optimal, how/why to determine what is memory or
throughput limited

### Optimal under the roofline model

```
ideal piece of code (on hardware configuration)
```

<!-- Roofline plot of optimal -->

<!-- Perf disassembly of optimal to show ratios -->

### Memory bandwidth limited

```
Memory bandwidth limited piece kernel (on hardware configuration)
```

<!-- Roofline plot of limited -->

<!-- Perf disassembly plot of limited -->

```
optimised piece of code
```

<!-- Roofline plot of optimal -->

### Floating point throughput limited

<!-- Roofline plot of limited -->

<!-- Perf disassembly plot of limited -->

```
optimised piece of code
```

<!-- Roofline plot of optimal -->

## Differences across hardware configurations

<!-- -->

## Extensions to the roofline model

### Cache-aware roofline models

### GPU roofline models

<!-- -->

## Glossary

<!-- -->

## References
