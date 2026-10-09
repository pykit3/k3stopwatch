"""
StopWatch operates on a notion of "spans" which represent scopes of code for which we
want to measure timing. Spans can be nested and placed inside loops for aggregation.

StopWatch requires a root scope which upon completion signifies the end of the round
of measurements. On a server, you might use a single request as your root scope.

StopWatch produces two kinds of reports.
1) Aggregated (see _reported_values).
2) Non-aggregated or "tracing" (see _reported_traces).
"""

from .k3stopwatch import (
    StopWatch,
    TimerData,
    default_export_aggregated_timers,
    default_export_tracing,
    format_report,
)

__all__ = [
    "StopWatch",
    "TimerData",
    "default_export_aggregated_timers",
    "default_export_tracing",
    "format_report",
]


def __getattr__(name: str) -> str:
    # importlib.metadata takes about 20 ms to import, so it is loaded only
    # when __version__ is read
    if name != "__version__":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib.metadata import version

    return version("k3stopwatch")
