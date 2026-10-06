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
