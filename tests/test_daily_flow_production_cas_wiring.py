import ast
import copy
import os
import tempfile
import threading
import time as system_time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
BUSINESS_DATE = "2026-08-04"
FUTURE_HOST_DATE = "2026-08-05"
TRUSTED_SHARE_TARGET = "1000000001"
TRUSTED_SHARE_VERIFIED_AT = "2026-08-04T09:10:11+0800"
TRUSTED_SHARE_REASON = "verified-direct-contact-send-v2"


DAILY_FLOW_FUNCTIONS = (
    "_daily_business_date",
    "_daily_flow_status_paths",
    "_daily_flow_commit",
    "_daily_flow_mark_status",
    "_daily_flow_mark_failure",
    "_daily_flow_repair_unverified_status",
)


def load_functions(*names):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    wanted = set(names)
    nodes = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted
    ]
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace


class _FutureHostClock:
    """Host clock fixture: the runtime clock is a day ahead of business day."""

    def time(self):
        return 0.0

    def localtime(self, value=None):
        return system_time.localtime(0.0 if value is None else float(value))

    def strftime(self, format_string, value=None):
        if format_string == "%Y-%m-%d":
            return FUTURE_HOST_DATE
        return FUTURE_HOST_DATE + "T00:00:00+0800"


class _StrictVersionedStatusStore:
    """Versioned replace-only store that exposes stale write clobbers.

    The writer intentionally does not merge ``flows``.  The production
    ``_daily_flow_commit`` default CAS is responsible for taking the versioned
    path; direct status writes retain their stale snapshot and overwrite it.
    """

    def __init__(self, data, before_plain_write=None):
        self._lock = threading.RLock()
        self._data = copy.deepcopy(data)
        self._data.setdefault("_revision", 0)
        self._before_plain_write = before_plain_write

    @staticmethod
    def _revision(data):
        try:
            return int(data.get("_revision", 0) or 0)
        except (AttributeError, TypeError, ValueError):
            return 0

    def read_status(self, path):
        del path
        with self._lock:
            return copy.deepcopy(self._data)

    def write_status(self, path, payload):
        del path
        candidate = copy.deepcopy(payload)
        with self._lock:
            current_revision = self._revision(self._data)
        is_cas_commit = (
            self._revision(candidate) == current_revision + 1
        )
        if not is_cas_commit and callable(self._before_plain_write):
            self._before_plain_write(candidate)
        with self._lock:
            self._data = candidate
        return True

    def snapshot(self):
        with self._lock:
            return copy.deepcopy(self._data)


class DailyFlowProductionCasWiringRedTests(unittest.TestCase):
    def build_namespace(self):
        namespace = load_functions(*DAILY_FLOW_FUNCTIONS)
        clock = _FutureHostClock()
        namespace.update({
            "os": os,
            "time": clock,
            "__file__": str(HOOK),
            "_DAILY_BUSINESS_DATE_SOURCE": lambda: BUSINESS_DATE,
            "_daily_retry_max_default": lambda value=None: 3,
        })
        self.assertEqual(FUTURE_HOST_DATE, clock.strftime("%Y-%m-%d"))
        return namespace

    def join_threads(self, threads):
        for thread in threads:
            thread.join(timeout=5.0)
        for thread in threads:
            self.assertFalse(thread.is_alive(), thread.name + " did not finish")

    def test_mark_status_retries_stale_task_share_crossing_and_keeps_both(self):
        """Real status marks must traverse the versioned CAS, not writer merge."""
        namespace = self.build_namespace()
        task_plain_write_done = threading.Event()

        def order_plain_writes(payload):
            name = threading.current_thread().name
            if name == "status-share":
                if not task_plain_write_done.wait(timeout=3.0):
                    raise AssertionError("task plain write did not complete first")
            elif name == "status-task":
                task_plain_write_done.set()

        store = _StrictVersionedStatusStore(
            {"date": BUSINESS_DATE, "flows": {}},
            before_plain_write=order_plain_writes,
        )
        initial_reads = threading.Barrier(2)
        first_read_names = {"status-task", "status-share"}
        blocked_reads = set()
        blocked_reads_lock = threading.Lock()

        def stale_read_status(path):
            snapshot = store.read_status(path)
            name = threading.current_thread().name
            with blocked_reads_lock:
                block_this_read = (
                    name in first_read_names and name not in blocked_reads
                )
                if block_this_read:
                    blocked_reads.add(name)
            if block_this_read:
                try:
                    initial_reads.wait(timeout=3.0)
                except threading.BrokenBarrierError as error:
                    raise AssertionError("both stale status reads must rendezvous") from error
            return snapshot

        namespace["_daily_flow_read_status"] = stale_read_status
        namespace["_daily_flow_write_status"] = store.write_status
        results = {}
        errors = []
        with tempfile.TemporaryDirectory() as temp_dir:
            status_path = str(Path(temp_dir) / "daily_flow_status.json")

            def mark(flow, reason, verified_at):
                try:
                    results[flow] = namespace["_daily_flow_mark_status"](
                        flow,
                        "success",
                        target=TRUSTED_SHARE_TARGET if flow == "share" else "",
                        paths=[status_path],
                        today=BUSINESS_DATE,
                        verified_at=verified_at,
                        reason=reason,
                    )
                except BaseException as error:
                    errors.append((flow, error))

            threads = [
                threading.Thread(
                    target=mark,
                    args=(
                        "task",
                        "verified-task-claim-v1",
                        "2026-08-04T09:00:00+0800",
                    ),
                    name="status-task",
                ),
                threading.Thread(
                    target=mark,
                    args=("share", TRUSTED_SHARE_REASON, TRUSTED_SHARE_VERIFIED_AT),
                    name="status-share",
                ),
            ]
            for thread in threads:
                thread.start()
            self.join_threads(threads)

        self.assertEqual([], errors)
        self.assertEqual({"task": True, "share": True}, results)
        persisted = store.snapshot()
        self.assertEqual(BUSINESS_DATE, persisted.get("date"))
        self.assertEqual({"task", "share"}, set(persisted.get("flows") or {}))
        self.assertEqual(
            "success", persisted["flows"]["task"].get("status")
        )
        self.assertEqual(
            "success", persisted["flows"]["share"].get("status")
        )
        self.assertEqual(2, persisted.get("_revision"))

    def test_mark_failure_rebases_two_stale_task_attempts_to_two(self):
        """Two stale task failures must each consume one retry attempt."""
        namespace = self.build_namespace()
        first_plain_failure_done = threading.Event()

        def order_plain_writes(payload):
            del payload
            name = threading.current_thread().name
            if name == "failure-two":
                if not first_plain_failure_done.wait(timeout=3.0):
                    raise AssertionError("first plain failure did not complete first")
            elif name == "failure-one":
                first_plain_failure_done.set()

        store = _StrictVersionedStatusStore(
            {"date": BUSINESS_DATE, "flows": {}},
            before_plain_write=order_plain_writes,
        )
        initial_reads = threading.Barrier(2)
        first_read_names = {"failure-one", "failure-two"}
        blocked_reads = set()
        blocked_reads_lock = threading.Lock()

        def stale_read_status(path):
            snapshot = store.read_status(path)
            name = threading.current_thread().name
            with blocked_reads_lock:
                block_this_read = (
                    name in first_read_names and name not in blocked_reads
                )
                if block_this_read:
                    blocked_reads.add(name)
            if block_this_read:
                try:
                    initial_reads.wait(timeout=3.0)
                except threading.BrokenBarrierError as error:
                    raise AssertionError("both stale failure reads must rendezvous") from error
            return snapshot

        namespace["_daily_flow_read_status"] = stale_read_status
        namespace["_daily_flow_write_status"] = store.write_status
        results = {}
        errors = []
        with tempfile.TemporaryDirectory() as temp_dir:
            status_path = str(Path(temp_dir) / "daily_flow_status.json")

            def mark_failure(label):
                try:
                    results[label] = namespace["_daily_flow_mark_failure"](
                        "task",
                        reason=label,
                        paths=[status_path],
                        today=BUSINESS_DATE,
                        now_epoch=0.0,
                    )
                except BaseException as error:
                    errors.append((label, error))

            threads = [
                threading.Thread(
                    target=mark_failure,
                    args=("failure-one",),
                    name="failure-one",
                ),
                threading.Thread(
                    target=mark_failure,
                    args=("failure-two",),
                    name="failure-two",
                ),
            ]
            for thread in threads:
                thread.start()
            self.join_threads(threads)

        self.assertEqual([], errors)
        self.assertEqual({"failure-one": True, "failure-two": True}, results)
        persisted = store.snapshot()
        task = persisted["flows"]["task"]
        self.assertEqual(BUSINESS_DATE, persisted.get("date"))
        self.assertEqual(BUSINESS_DATE, task.get("date"))
        self.assertEqual("failed", task.get("status"))
        self.assertEqual(2, task.get("attempts"))
        self.assertEqual(2, persisted.get("_revision"))

    def test_trusted_share_success_survives_stale_pending_failure_and_repair(self):
        """Old share snapshots cannot replace a direct-send proof for the day."""
        namespace = self.build_namespace()
        pending_plain_write_done = threading.Event()
        failure_plain_write_done = threading.Event()

        def order_plain_writes(payload):
            del payload
            name = threading.current_thread().name
            if name == "stale-failure":
                if not pending_plain_write_done.wait(timeout=3.0):
                    raise AssertionError("stale pending write did not complete first")
                failure_plain_write_done.set()
            elif name == "stale-repair":
                if not failure_plain_write_done.wait(timeout=3.0):
                    raise AssertionError("stale failure write did not complete first")
            elif name == "stale-pending":
                pending_plain_write_done.set()

        pending_snapshot = {
            "_revision": 0,
            "date": BUSINESS_DATE,
            "flows": {
                "share": {
                    "date": BUSINESS_DATE,
                    "status": "pending",
                    "verified_at": "2026-08-04T08:30:00+0800",
                    "reason": "stale-pending",
                },
            },
        }
        recovery_snapshot = {
            "_revision": 0,
            "date": BUSINESS_DATE,
            "flows": {
                "share": {
                    "date": BUSINESS_DATE,
                    "status": "success",
                    "verified_at": "2026-08-04T08:31:00+0800",
                    "reason": "seeded-from-daily-counters",
                },
            },
        }
        store = _StrictVersionedStatusStore(
            pending_snapshot,
            before_plain_write=order_plain_writes,
        )
        stale_snapshots = {
            "stale-pending": pending_snapshot,
            "stale-failure": pending_snapshot,
            "stale-repair": recovery_snapshot,
        }
        stale_started = {
            name: threading.Event() for name in stale_snapshots
        }
        release_stale_submissions = threading.Event()
        blocked_reads = set()
        blocked_reads_lock = threading.Lock()

        def delayed_old_snapshot(path):
            name = threading.current_thread().name
            with blocked_reads_lock:
                block_this_read = (
                    name in stale_snapshots and name not in blocked_reads
                )
                if block_this_read:
                    blocked_reads.add(name)
            if block_this_read:
                snapshot = copy.deepcopy(stale_snapshots[name])
                stale_started[name].set()
                if not release_stale_submissions.wait(timeout=3.0):
                    raise AssertionError("trusted share success was not committed")
                return snapshot
            return store.read_status(path)

        namespace["_daily_flow_read_status"] = delayed_old_snapshot
        namespace["_daily_flow_write_status"] = store.write_status
        outcomes = {}
        errors = []
        with tempfile.TemporaryDirectory() as temp_dir:
            status_path = str(Path(temp_dir) / "daily_flow_status.json")

            def invoke(label, function):
                try:
                    outcomes[label] = function()
                except BaseException as error:
                    errors.append((label, error))

            threads = [
                threading.Thread(
                    target=invoke,
                    args=(
                        "pending",
                        lambda: namespace["_daily_flow_mark_status"](
                            "share",
                            "pending",
                            paths=[status_path],
                            today=BUSINESS_DATE,
                            verified_at="2026-08-04T09:11:00+0800",
                            reason="stale-pending-submit",
                        ),
                    ),
                    name="stale-pending",
                ),
                threading.Thread(
                    target=invoke,
                    args=(
                        "failure",
                        lambda: namespace["_daily_flow_mark_failure"](
                            "share",
                            reason="stale-failure-submit",
                            paths=[status_path],
                            today=BUSINESS_DATE,
                            now_epoch=0.0,
                        ),
                    ),
                    name="stale-failure",
                ),
                threading.Thread(
                    target=invoke,
                    args=(
                        "repair",
                        lambda: namespace["_daily_flow_repair_unverified_status"](
                            paths=[status_path],
                            counter_paths=[],
                            today=BUSINESS_DATE,
                        ),
                    ),
                    name="stale-repair",
                ),
            ]
            for thread in threads:
                thread.start()
            for name, started in stale_started.items():
                self.assertTrue(started.wait(timeout=3.0), name + " did not read its old snapshot")

            self.assertTrue(namespace["_daily_flow_mark_status"](
                "share",
                "success",
                target=TRUSTED_SHARE_TARGET,
                paths=[status_path],
                today=BUSINESS_DATE,
                verified_at=TRUSTED_SHARE_VERIFIED_AT,
                reason=TRUSTED_SHARE_REASON,
            ))
            release_stale_submissions.set()
            self.join_threads(threads)

        self.assertEqual([], errors)
        self.assertEqual({"pending", "failure", "repair"}, set(outcomes))
        persisted = store.snapshot()
        self.assertEqual(BUSINESS_DATE, persisted.get("date"))
        share = persisted["flows"]["share"]
        self.assertEqual(
            {
                "status": "success",
                "target": TRUSTED_SHARE_TARGET,
                "verified_at": TRUSTED_SHARE_VERIFIED_AT,
                "reason": TRUSTED_SHARE_REASON,
            },
            {
                "status": share.get("status"),
                "target": share.get("target"),
                "verified_at": share.get("verified_at"),
                "reason": share.get("reason"),
            },
        )


if __name__ == "__main__":
    unittest.main()
