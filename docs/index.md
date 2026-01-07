# k3stopwatch

[![Action-CI](https://github.com/pykit3/k3stopwatch/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3stopwatch/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3stopwatch/badge/?version=stable)](https://k3stopwatch.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3stopwatch)](https://pypi.org/project/k3stopwatch)

Hierarchical timing measurement with aggregated and tracing reports.

StopWatch operates on "spans" representing code scopes for timing measurement.
Spans can be nested and placed inside loops for aggregation.

k3stopwatch is a component of [pykit3](https://github.com/pykit3) project: a python3 toolkit set.

## Installation

```bash
pip install k3stopwatch
```

## Quick Start

```python
import k3stopwatch

sw = k3stopwatch.StopWatch()

with sw.timer('root'):
    with sw.timer('task_a'):
        # do some work
        pass

    for i in range(10):
        with sw.timer('loop_iteration'):
            # timed loop
            pass

# Get timing reports
print(k3stopwatch.format_report(sw.get_last_aggregated_report()))
```

## API Reference

::: k3stopwatch

## License

The MIT License (MIT) - Copyright (c) 2015 Zhang Yanpo (张炎泼)
