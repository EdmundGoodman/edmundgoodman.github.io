---
title: "Performance Profiling at the Bytecode level in CPython"
author: "Edmund Goodman"
date: 2025-06-23T00:11:54+01:00
math: true
draft: true
---

{{< note title="A note on provenance" >}}
I developed the ByteSight tool as part of my MPhil research project, titled
"Performance and Dynamism in User-extensible Compiler Infrastructures". This
blog post is derived from the fourth and eighth chapters of my thesis describing
this research.
{{< /note >}}

Performance profilers are powerful tools that provide useful information about
program control flow and hotspots, facilitating performance optimisation.
Our research requires detailed information instrumenting Python's internal
evaluation loop to draw comparisons with the C++ language runtime and
characterise the cost of dynamism. However, existing profilers do not provide
information at this granularity, motivating our work in this area. In this post
we present ByteSight, a novel tool for performance profiling at the bytecode
level, allowing us to look deeper into the performance characteristics of highly
dynamic programs whose implementation cannot easily be deferred into lower level
languages.

<!--more-->

Recent developments to CPython's runtime motivate collecting more fine-grained
profiling information. For example, the specialising adaptive interpreter
rewrites bytecode at runtime into quickened forms, and the baseline JIT
substitutes bytecode for tier two micro-operations -- both yielding performance
characteristics which cannot be reasoned about with function or line level
instrumentation. In addition to this, bytecode performance profiling information
helps provide a key missing data point when examining the impact of program
dynamism. However, to the author's knowledge, no profilers exist which support
measurement at this granularity
([Related work]({{<ref "#related-work" >}})).
One reason for this conspicuous absence of bytecode level profilers is the
difficulty of measuring their very short execution times, in the order of the
highest resolution system counter. This difficulty is further worsened by the
bytecode dispatch and evaluation being deeply interleaved within the
interpreter's execution loop.

ByteSight, our novel tool for the performance profiling of CPython bytecode,
addresses this gap in the existing provision. ByteSight is a tracing profiler
which operates on the bytecode level of the Python interpreter. It is
implemented natively in Python using only the standard library, and its source
code is available under the MIT licence on GitHub [^1]. It does not require
patches to Python's language implementation. This makes it portable, robust
across language versions, and simple to install from the Python Package Index
(PyPI). In this blog post, we discuss its implementation and provide examples of
its use.

## Implementation

By virtue of the flexibility and dynamism of its interpreter's implementation,
CPython provides a wide variety of opportunities for instrumenting and
introspecting running code. One example of this is the standard library function
`sys.settrace`, which associates dynamic, user-defined callback functions with
the dispatch of key virtual machine events. These include function calls, line
execution, handling exceptions, and even individual bytecode operations
(interchangeably referred to as opcodes in the documentation). This callback
function receives the event type along with the CPython frame and code objects
currently being evaluated by the interpreter, facilitating precise
instrumentation of the internal operation of the interpreter. Other
possibilities for collecting this information include making custom patches to
the CPython implementation, or leveraging the `LLTRACE` feature of the debug
build of Python. However, the former is specific to individual language
versions, and the latter has a verbose output containing no performance
information. Furthermore, both requiring re-compiling the CPython implementation
from source, precluding simple installation by users from PyPI. As such, we
chose to leverage `sys.settrace`, accepting the challenges associated with its
measurement for benefits it provides in portability and robustness across
language versions.

Our tool captures bytecode level profiling information through a custom callback
function which records a sequence of timestamps associated with the traced
events. From this set of timestamps, we can calculate the execution duration of
each emitted opcode. This constitutes profiling information of a higher
granularity than existing Python performance profilers. In spite of its name, we
leverage the `sys.settrace` function as opposed to its sister function
`sys.setprofile`. We do this because `sys.settrace` has supported emitting trace
events for opcodes since Python 3.7, whereas `sys.setprofile` only emits events
at the function granularity. This approach of leveraging CPython's API provides
benefits of robustness across versions and easy installation, but also causes a
number of challenges for accurate and precise measurement of very short events.

These challenges come as a result of the callback function itself being a
callable Python code object. As such, the infrastructure to invoke and evaluate
this function has a significant performance cost, in many cases taking longer
than the opcode it is instrumenting. To mitigate this, our custom tracing
function (Listing \ref{listing:profiling-trace-function}) records the timestamp
at the earliest point \circledbase{pairedOneLightBlue}{1} and the latest point
\circledbase{pairedFourDarkGreen}{4}, allowing the majority of its overhead to
be excluded. Properties of the frame are then set to emit events for opcodes but
not lines \circledbase{pairedTwoDarkBlue}{2}, further avoiding extraneous
overhead. Finally, a tuple of timestamps for the end of the last trace function
and the start of the current one are recorded
\circledbase{pairedThreeLightGreen}{3}, upper bounding the duration of opcode
execution. This sequence of recorded timestamps can then be used in combination
with domain knowledge of the language runtime to calculate individual opcode
durations.

```python
def _trace__collect_event_timestamps(
    self, frame: types.FrameType, event: str, _arg: Any
) -> Callable[..., Any] | None:
    """Trace function to collect opcode timestamps."""
    now_timestamp = perf_counter() £\circledbase{pairedOneLightBlue}{\footnotesize{1}}£

    frame.f_trace_lines = False £\circledbase{pairedTwoDarkBlue}{\footnotesize{2}}£
    frame.f_trace_opcodes = True

    if event == "opcode":
        self._timestamps.append( £\circledbase{pairedThreeLightGreen}{\footnotesize{3}}£
            (
                self._prev_event_timestamp,
                now_timestamp,
            )
        )
        self._prev_event_timestamp = perf_counter()  £\circledbase{pairedFourDarkGreen}{\footnotesize{4}}£

    return self._trace__collect_event_timestamps
```
<!-- \caption{Trace callback function generating a sequence of timestamps instrumenting opcode events.} -->

## CPython internals

In order to infer opcode durations from the event timestamps emitted tracing
function, we must first examine the language runtime implementation with which
it is co-designed. In this section, we present a view of CPython 3.10's
implementation as a basis for our profiler. In more recent Python versions such
as CPython 3.13, aspects of the tracing infrastructure have been refactored.
However, since both the API provided by the standard library and the position of
the tracing logic in the evaluation loop remain the same, the procedure remains
applicable to these newer versions. Code objects in CPython are executed by the
`_PyEval_EvalFrameDefault` function (Listing
\ref{listing:cpython-evaluation-overview-code}). This begins with initialisation
to ready for evaluation \circledbase{pairedOneLightBlue}{a}, then enters an
unbounded evaluation loop \circledbase{pairedTwoDarkBlue}{b}. This loop decodes
the next bytecode instruction \circledbase{pairedThreeLightGreen}{c}, then
switches on it to select the appropriate logic to execute
\circledbase{pairedFourDarkGreen}{d}, and repeats until an exception is thrown
or the code object terminates. Having an understanding of the evaluation loop,
we can next discuss how it is instrumented.

```text
PyObject* _PyEval_EvalFrameDefault(PyThreadState *tstate, PyFrameObject *f, int throwflag) {
    // ... declarations and initialization of local variables, macros definitions, call depth handling, ...  £\circledbase{pairedOneLightBlue}{\scriptsize{a}}£
    // ... code for tracing call event

    for (;;) {  £\circledbase{pairedTwoDarkBlue}{\scriptsize{b}}£
        // NEXTOPARG() macro  £\circledbase{pairedThreeLightGreen}{\scriptsize{c}}£
        _Py_CODEUNIT word = *next_instr;
        opcode = _Py_OPCODE(word);
        oparg = _Py_OPARG(word);
        next_instr++;

        // ... code for tracing opcode events

        switch (opcode) {    £\circledbase{pairedFourDarkGreen}{\scriptsize{d}}£
            case TARGET(NOP) {
                FAST_DISPATCH();
            }
            case TARGET(LOAD_FAST) {
                // ... code for loading local variable
            }
            // ... 117 more cases for every possible opcode
        }
    }
    // ... termination
}
```
<!-- \caption{C implementation snippets, derived from an explanation of the bytecode evaluation by Victor Skvortsov \cite{victorskvortsovPythonScenes42020}.} -->

{{< figure
    src="/images/posts/bytecode_profiling_python/python_eval.drawio.png"
    alt="Control flow between evaluation (blue) and tracing (green)."
    caption="Control flow between evaluation (blue) and tracing (green)." >}}

<!-- \caption{Control flow between evaluation (blue) and tracing (green).} -->
<!-- \caption{Overview of the evaluation loop of CPython 3.10, showing components relating to bytecode evaluation and tracing.} -->

CPython's tracing mechanism works in two phases: registering the callback
function, and the invocation of this callback function from the evaluation loop.
To register the callback function, users can invoke `sys.settrace`, a standard
library function binding to the C implementation of `sys_settrace` in
`sysmodule.c`. This in turn invokes `_PyEval_SetTrace` in `ceval.c`, which
updates two fields on the Python GIL thread state struct: `c_traceobj` and
`c_tracefunc`. The former is a callable Python code object for the callback
function, and the latter points to a ``trampoline'' function, which invokes this
code object with the current frame information. This trampoline is then invoked
when events occur in the evaluation loop, including at the start of the frame
evaluation for functions, after each opcode is extracted, and on returning from
the function (green blocks in
\autoref{figure:cpython-evaluation-overview-block}).

### Inferring bytecode duration

Given both the sequence of timestamps and an understanding of their place in
CPython's evaluation loop, we can infer our profiler's goal of the time taken to
execute each opcode. One way to visualise this is by flattening the block
diagram of the evaluation loop
(\autoref{figure:cpython-evaluation-overview-block}) and annotating it with
timestamp measurements (\autoref{figure:profiler-run}). From this, we can then
construct a system of equations relating the measurements, and derive the
durations of each opcode.

{{< figure
    src="/images/posts/bytecode_profiling_python/untraced_run.drawio.png"
    alt="Timing function runtime without opcode event tracing."
    caption="Timing function runtime without opcode event tracing." >}}

{{< figure
    src="/images/posts/bytecode_profiling_python/traced_run.drawio.png"
    alt="Timing function runtime, including recording timestamps at the start and end of each opcode event."
    caption="Timing function runtime, including recording timestamps at the start and end of each opcode event." >}}

<!-- \caption{Timing Python's evaluation loop with and without instrumentation of opcode events using `sys.settrace`.} -->

By examination of where trace timestamps are recorded, we can see that the
duration of the n{{< raw_html >}}<sup>th</sup>{{< /raw_html >}} bytecode
instruction, \(b_n\), is equal to the difference between the recorded timestamp
pairs, \(o_n\), and the fixed overheads before and after the tracing function,
\(\alpha\) and \(\omega\) respectively.

\begin{equation}
    \label{eq:bn_examination}
    b_n = o_n - (\alpha + \omega)
\end{equation}

Furthermore, the measured runtime of the instrumented function, \(T_I\), is equal
to the sum of the uninstrumented runtime \(T_U\) and the overhead incurred by
tracing.

\begin{equation}
    \label{eq:ti_examination}
    T_I = T_U + \sum_{n} (\alpha + \omega + t_n)
\end{equation}

As such, we calculate the sum of the overheads before and after the tracing
function, \(\alpha + \omega\), under the assumption that they are fixed. This
assumption is justified by the calling infrastructure for the tracing function
being the same across all opcodes.

\begin{equation}
    \label{eq:ao_inferred}
    \alpha + \omega = \frac{T_I - T_U - \sum_{n} t_n}{n}
\end{equation}

Finally, we can combine this with our initial observation to infer our goal of
opcode duration.

\begin{equation}
    \label{eq:bn_inferred}
    b_n = o_n - \frac{T_I - T_U - \sum_{n} t_n}{n}
\end{equation}

Beyond the careful co-design of the tracing measurement logic with CPython's
implementation, there are a number of confounding effects which must be
mitigated to ensure accurate measurement. Firstly, for the profiling information
to be useful, the resolution of the most accurate system clock must be
sufficient to resolve differences bytecode execution time. On our experimental
hardware (\autoref{ssec:experimental-setup}) this was true, having a \(1\)ns
timer able to resolve differences in opcodes taking around \(10\)ns to execute.
However, this is not the case for modern Apple Silicon devices. Their most
accurate system timer, `mach_absolute_time` \cite{appleinc.Mach_absolute_time},
has a resolution of only \(40\)ns and is hence unable to resolve individual
bytecode instruction durations of approximately \(10\)ns. This is a physical
limitation on measuring such necessarily fast events, and as such can only be
resolved by selecting appropriate hardware. Secondly, the CPython language
runtime periodically runs housekeeping tasks such as garbage collection,
disrupting the flow of bytecode execution and hence adding random noise to our
measurements. These can effects can be minimised using techniques from existing
performance measurement work such as `timeit`
\cite{pythonsoftwarefoundationTimeitMeasureExecution} or `pyperf`
\cite{victorstinnerPsfPyperf2025}, for example by disabling garbage collection
for the duration of profiling. Finally, we repeat and aggregate our experimental
measurements for statistical confidence, further minimising machine noise to
ensure clean and reliable profiling results.

## Example usage

Having implemented our profiler, we can demonstrate its capabilities on an
example workload (Listing \ref{listing:profiler-example}). Each traced event is
displayed on its own line, in combination showing the exact sequence of
instructions performed by the interpreter when evaluating the function. Function
invocations, such as calling `inner_function`
\circledbase{pairedOneLightBlue}{x}, are indented by their call stack depth for
easy readability. In addition to this, bytecode instructions are formatted
following the convention of the standard library, but are annotated with their
duration in a comment on the right-hand side of the trace
\circledbase{pairedTwoDarkBlue}{y}.


```python
import bytesight

def inner_function(
    x: int | str | float
) -> None:
    assert x

def example_function():
    inner_function(1)
    pass
    _x = perf_counter()

bytesight.profile_bytecode(
    example_function
)
```
<!-- \caption{Python program.} -->

```text
// ======= example:8 `example_function` ========
// >>> inner_function(1)
7           0   LOAD_GLOBAL          0   (inner_function)   // 15   ns
            2   LOAD_CONST           1   (1)                // 15   ns
            4   CALL_FUNCTION        1   ()                 // 31   ns

    // ======== example:3 `inner_function` ========= £\circledbase{pairedOneLightBlue}{\scriptsize{x}}£
    // >>> assert x
    4           0   LOAD_FAST            0   (x)            // 13   ns
                2   POP_JUMP_IF_TRUE     4   (to 8)         // 13   ns
            >>  8   LOAD_CONST           0   (None)         // 12   ns
                10  RETURN_VALUE             ()             // 31   ns
    // =============================================

            6   POP_TOP                  ()                 // 16   ns
// >>> pass
8           8   NOP                      ()                 // 15   ns £\circledbase{pairedTwoDarkBlue}{\scriptsize{y}}£
// >>> _x = perf_counter()
9           10  LOAD_GLOBAL          1   (perf_counter)     // 15   ns
            12  CALL_FUNCTION        0   ()                 // 17   ns
            14  STORE_FAST           0   (_x)               // 14   ns
            16  LOAD_CONST           0   (None)             // 13   ns
            18  RETURN_VALUE             ()                 // 28   ns
// =============================================
```
<!-- \caption{Profiler output.} -->
<!-- \caption{Output of the bytecode profiling tool for a simple Python program, showing the sequence of dispatched bytecode and their individual execution times.} -->

## Related work

Driven by Python's immense popularity, significant research effort has been
expended developing tools and techniques to characterise its performance. This
section discusses a relevant subset of these approaches, and contrasts them with
our novel contributions.

### Measuring application performance in Python

Reliable and accurate performance measurement is notoriously difficult. As such,
its careful execution constitutes the main contribution of systems papers and
theses \cite{crapeperformance} \cite{harris2021understanding}. This difficulty
comes from both sides of the hardware-software interface. For example, hardware
optimisations such as hierarchical caches, branch predictors, and power
management schemes exhibit complex emergent behaviour
\cite{hennessyComputerArchitectureQuantitative2012}, making performance
measurements less predictable and consistent. Similar confounding effects come
from software, from process scheduling in the operating system to garbage
collection in language runtimes \cite{blackburnMythsRealitiesPerformance2004}.
Beyond this, advanced interpreters leverage runtime performance information for
adaptive specialisation and JIT compilation, further muddling measurements. This
phenomenon is explored by Barrett et al.'s "Virtual Machine Warmup Blows Hot and
Cold" \cite{barrettVirtualMachineWarmup2017}, where interpreter virtual machine
warmup is shown to be highly variable, with benchmarks taking over 2000
iterations to reach a steady state. As such, accurate measurement of the
performance characteristics of a Python program is more involved than the
na\"ive approach of taking the wall time it takes to execute -- requiring
additional tools and techniques to guarantee reliable results. Fortunately,
Python's strong ecosystem provides a wide variety of tools to achieve this goal,
from the simple standard library `timeit` utility
\cite{pythonsoftwarefoundationTimeitMeasureExecution} to the `pyperf` package
\cite{victorstinnerPsfPyperf2025}, with more complex control over confounding
effects such as warm-ups and CPU isolation. Our work leverages these tools to
make accurate measurements of compiler framework performance.

A key contribution of our research is our application of these tools to produce
robust performance measurements and analysis of the xDSL user-extensible
compiler frameworks, extending and contrasting similar work for MLIR. In
addition to the research contribution of these measurements themselves, our work
further supports ongoing research using the xDSL framework by providing
re-usable performance benchmarks and associated tooling to measure performance.
However, sometimes measurements with finer than end-to-end granularity are
required. As such, our tooling also provides a simple user interface for
applying performance profilers to these benchmarks.

### Profiling to understand Python's performance

Existing profilers for Python typically operate at the function level. For
example, Python's standard library provides the `profile` module, a
Python-native tracing profiler, along with `cProfile`, a more performant C
implementation of the same functionality
\cite{pythonsoftwarefoundationPythonProfilers}. These instrument each call
event, providing accurate profiling information for each evaluated function.
Beyond the standard library, profilers such as `pyinstrument` use statistical
sampling rather than tracing to reduce overhead incurred by performance
measurement \cite{rickerbyPyinstrument2025}. In addition to this, the recent
OSDI best paper winner ``Triangulating Python Performance Issues with SCALENE''
\cite{bergerTriangulatingPythonPerformance2023a} introduces another profiler
which focusses on the FFI boundary between C and Python, a key bottleneck for
the best practice of delegating computation to fast low-level implementations.
This delegation is particularly effective for structured workloads such as
linear algebra, but is less suitable for highly dynamic workloads. Furthermore,
profiling information at a finer granularity than the function level is often
needed to deeply the performance of a program. `line_profiler` provides this
functionality to a line level \cite{robertkernPyutilsLine_profiler2025}, but
this is still one level of abstraction over the increasingly complex
implementation of CPython's interpreter.

We fill this gap in the existing provision with ByteSight, a Python-native
tracing performance profiler at the bytecode level. ByteSight extends existing
work outputting and rewriting bytecode sequences
\cite{0xecCodingReversingHacking2017}
\cite{clementrouaultUnderstandingPythonExecution}
\cite{nedbatchelderWickedHackPython2008}, providing an easily installable
package with the novel capability of performance profiling individual bytecode
instructions. This contribution also unblocks other work in this thesis,
facilitating close examination of specialised implementations and providing
information about the performance of individual dynamic bytecode instructions.

## Summary

ByteSight provides straightforward mechanism to show the bytecode trace of any
Python function. This facilitates debugging control flows in highly dynamic
code, which often suffer from ``spooky action at a distance'', and is
educational for the internal workings of Python's interpreter. This
functionality is easily accessible by installation from PyPI, contrasting
previous approaches which required either re-compiling the Python interpreter or
manually implementing the same approach each time. Beyond this, the profiling
information of the duration of each opcode is not provided by any existing tools
to the author's knowledge. This information provides insight into the
relationship between performance and dynamism in Python, and is more generally
helpful for understanding and optimising performance critical code which cannot
be deferred to a low-level language through FFI bindings.

## References

[^1]: https://github.com/EdmundGoodman/bytesight
