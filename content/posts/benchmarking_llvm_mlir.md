---
title: "Benchmarking LLVM MLIR"
author: "Edmund Goodman"
date: 2025-04-09T17:01:44+01:00
---

At the 2024 European LLVM Developers' Meeting, Mehdi Amini and Jeff Nui
presented their keynote talk "How Slow is MLIR" [^1]. This presented
micro-benchmarks for key operations in the MLIR compiler, such as traversing the
IR and creating operations. However, the code for the benchmarks and
instructions for running them are not easily available online alongside the
talk. This blog post addresses this gap in the provision.

<!--more-->

## The benchmarks

By asking the in the LLVM discord and spelunking around GitHub, I found the
benchmarks discussed in this talk are available on a branch of Mehdi's fork of
LLVM [available here](https://github.com/joker-eph/llvm-project/tree/benchmarks),
with a diff with the main branch
[available here](https://github.com/llvm/llvm-project/compare/main...joker-eph:llvm-project:benchmarks).

## Running the benchmarks

To run the benchmarks, first clone the repository at the correct branch:

```bash
git clone -b benchmarks https://github.com/joker-eph/llvm-project/
```

Then, built the appropriate CMake target:

```bash
mkdir llvm-project/build
cd llvm-project/build
cmake -G Ninja ../llvm \
   -DLLVM_ENABLE_PROJECTS=mlir \
   -DLLVM_TARGETS_TO_BUILD="host" \
   -DLLVM_ENABLE_BENCHMARKS=ON \
   -DCMAKE_BUILD_TYPE=Release \
   -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
cmake --build . --target MLIR_IR_Benchmark
```

Finally, run the benchmarks:

```bash
./tools/mlir/unittests/Benchmarks/MLIR_IR_Benchmark
```

## References

[^1] <https://www.youtube.com/watch?v=7qvVMUSxqz4>
[^2] <https://llvm.org/devmtg/2024-04/slides/Keynote/Amini-Niu-HowSlowIsMLIR.pdf>
[^3] <https://mlir.llvm.org/>
[^4] <https://mlir.llvm.org/getting_started/>
