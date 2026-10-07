import os
import unittest

import k3ut

import k3stopwatch

dd = k3ut.dd

this_base = os.path.dirname(__file__)


class TestK3stopwatch(unittest.TestCase):
    foo_fn = "/tmp/foo"

    def _clean(self):
        # remove written file
        try:
            os.unlink(self.foo_fn)
        except OSError:
            pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_procerror(self):
        pass

    def test_end_time_zero(self):
        # The clock reads 10.0, so an `end_time` of 0 taken as absent would make the span 10 seconds long.
        sw = k3stopwatch.StopWatch(time_func=lambda: 10.0)
        sw.start("root", start_time=0)
        sw.end("root", end_time=0)

        report = sw.get_last_aggregated_report()
        self.assertEqual(0, report.root_timer_data.end_time)
        self.assertEqual({"root": [0.001, 1, None]}, report.aggregated_values)

    def test_strict_misuse(self):
        sw = k3stopwatch.StopWatch(strict_assert=True)
        self.assertRaises(RuntimeError, sw.end, "root")
        self.assertRaises(RuntimeError, sw.cancel, "root")

        sw.start("root")
        self.assertRaises(RuntimeError, sw.end, "other")

    def test_non_strict_end_on_empty_stack(self):
        sw = k3stopwatch.StopWatch(strict_assert=False)
        sw.end("root")

        self.assertIsNone(sw.get_last_aggregated_report())

    def test_nested(self):
        now = [0]
        sw = k3stopwatch.StopWatch(time_func=lambda: now[0])

        with sw.timer("root"):
            for _ in range(2):
                with sw.timer("child"), sw.timer("grandchild"):
                    now[0] += 1
            now[0] += 1

        report = sw.get_last_aggregated_report()
        self.assertEqual(
            {
                "root": [3000.0, 1, None],
                "root#child": [2000.0, 2, None],
                "root#child#grandchild": [2000.0, 2, None],
            },
            report.aggregated_values,
        )

        traces = sw.get_last_trace_report()
        names = {t.span_id: t.log_name for t in traces}
        spans = [(t.log_name, t.start_time, t.end_time, names.get(t.parent_span_id)) for t in traces]
        self.assertEqual(
            [
                ("root#child#grandchild", 0, 1, "root#child"),
                ("root#child", 0, 1, "root"),
                ("root#child#grandchild", 1, 2, "root#child"),
                ("root#child", 1, 2, "root"),
                ("root", 0, 3, None),
            ],
            spans,
        )

    def test_cancel(self):
        now = [0]
        sw = k3stopwatch.StopWatch(time_func=lambda: now[0])

        with sw.timer("root"):
            with sw.timer("cancelled"):
                now[0] += 1
                sw.cancel("cancelled")
            with sw.timer("kept"):
                now[0] += 1

        report = sw.get_last_aggregated_report()
        self.assertEqual({"root": [2000.0, 1, None], "root#kept": [1000.0, 1, None]}, report.aggregated_values)

        traces = sw.get_last_trace_report()
        trace_names = [t.log_name for t in traces]
        self.assertEqual(["root#kept", "root"], trace_names)

    def test_timer_after_cancel_of_same_name(self):
        now = [0]
        sw = k3stopwatch.StopWatch(time_func=lambda: now[0])

        sw.start("root")
        sw.start("a")
        sw.cancel("a")
        with sw.timer("a"):
            now[0] += 1
        sw.end("root")

        report = sw.get_last_aggregated_report()
        self.assertEqual({"root": [1000.0, 1, None], "root#a": [1000.0, 1, None]}, report.aggregated_values)

    def test_export(self):
        now = [0]
        exported_traces = []
        exported_reports = []

        sw = k3stopwatch.StopWatch(
            time_func=lambda: now[0],
            export_tracing_func=lambda reported_traces: exported_traces.append(reported_traces),
            export_aggregated_timers_func=lambda aggregated_report: exported_reports.append(aggregated_report),
        )

        with sw.timer("root"):
            with sw.timer("child"):
                now[0] += 1

            # Only the end of the root span exports.
            self.assertEqual([], exported_traces)
            self.assertEqual([], exported_reports)

        with sw.timer("root"):
            now[0] += 2

        trace_names = [[t.log_name for t in traces] for traces in exported_traces]
        self.assertEqual([["root#child", "root"], ["root"]], trace_names)

        aggregated_values = [r.aggregated_values for r in exported_reports]
        self.assertEqual(
            [
                {"root": [1000.0, 1, None], "root#child": [1000.0, 1, None]},
                {"root": [2000.0, 1, None]},
            ],
            aggregated_values,
        )
