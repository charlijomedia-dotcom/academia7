"""The batch supervisor, driven with a stand-in worker (no estimation anywhere).

The stand-in replaces only the Python interpreter the supervisor launches: it writes a
few marked payloads into the chain's local folder, as a real worker's RefitCache would,
and reports. Everything else is the real supervisor: scheduling, budget, periodic and
final verified commits to Drive, the session summary, the lease.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

COLAB = Path(__file__).resolve().parents[3] / "colab"
sys.path.insert(0, str(COLAB))
import r1_tierb as tb  # noqa: E402
import r1_tierb_supervisor as supervisor  # noqa: E402

FAKE_WORKER = textwrap.dedent('''\
    #!{python}
    import json, sys
    from pathlib import Path
    argv = sys.argv[1:]
    get = lambda flag: argv[argv.index(flag) + 1]
    task, fits_root = get("--task"), Path(get("--batch-fits"))
    slug = "".join(c if c.isalnum() else "_" for c in task).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    fits = fits_root / slug / "fits"
    for i in range(4):
        key = abs(hash((task, i))) % (16 ** 64)
        path = fits / f"{{key % 256:02x}}" / f"{{key:064x}}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({{"status": "adequate", "forecasts": {{"1": 1.0}},
                                    "r1_provenance": "re-estimated"}}))
    Path(get("--result")).write_text(json.dumps({{"walk": {{"completed": 4, "planned": 4}},
                                                 "estimations": {{"fit_and_forecast": 4}}}}))
    sys.exit(0)
''')


def _fake_python(tmp: Path) -> Path:
    path = tmp / "fakepy"
    path.write_text(FAKE_WORKER.format(python=sys.executable))
    path.chmod(0o755)
    return path


def _run(tmp: Path, batch: str, budget_hours: float, start_epoch: float) -> tuple[int, dict]:
    drive = tmp / "drive"
    code = supervisor.main([
        "--batch", batch, "--python", str(_fake_python(tmp)), "--code-dir", str(tmp),
        "--original", str(tmp), "--work", str(tmp / "work"), "--drive-root", str(drive),
        "--session", f"{batch}-test", "--start-epoch", str(start_epoch),
        "--budget-hours", str(budget_hours), "--reserve-minutes", "1",
        "--backup-minutes", "10", "--max-workers", "2", "--poll-seconds", "0.2"])
    summaries = list((tb.batch_root(drive, batch) / "sessions").glob("*/session_summary.json"))
    return code, json.loads(summaries[0].read_text())


def test_supervisor_commits_and_verifies_every_chain(tmp_path):
    import time
    code, summary = _run(tmp_path, "B3", 11.0, time.time())
    assert code == 0, summary
    assert summary["final_verification"] == "Drive checkpoints equal local payloads"
    root = tb.batch_root(tmp_path / "drive", "B3")
    for task in tb.batch_tasks("B3"):
        assert summary["outcomes"][task] == "complete"
        assert len(tb.committed_inventory(root / "checkpoints" / tb.slug(task))) == 4
    lease = json.loads(next((root / "leases").glob("*.json")).read_text())
    assert lease["released"] is not None
    assert not (tb.batch_root(tmp_path / "drive", "B1")).exists()   # never another batch


def test_supervisor_starts_nothing_without_budget_and_reports_it(tmp_path):
    import time
    code, summary = _run(tmp_path, "B1", 1.0, time.time() - 3600)     # budget used up
    assert code == 3
    assert summary["outcomes"] == {"T4.8:UNRATE|300:MSAR": "not started (budget)"}
    assert not list((tmp_path / "work" / "chains").glob("*/result-*.json"))


SLOW_WORKER = FAKE_WORKER.replace("sys.exit(0)\n", "import time\ntime.sleep(600)\nsys.exit(0)\n")
assert SLOW_WORKER != FAKE_WORKER


def test_a_hard_killed_session_stays_traceable_from_its_checkpoints(tmp_path):
    """SIGKILL the whole session after its first commit: no summary is ever written,
    yet the session, its committed work and its unreleased lease are all on record,
    and it is reported as interrupted, apart from sessions that terminated."""
    import os
    import signal
    import subprocess
    import time
    fake = tmp_path / "slowpy"
    fake.write_text(SLOW_WORKER.format(python=sys.executable))
    fake.chmod(0o755)
    drive = tmp_path / "drive"
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"scientific_commit": tb.SCIENTIFIC_PIN,
                                      "orchestration_commit": "f" * 40,
                                      "cache_identity": tb.CACHE_IDENTITY}))
    process = subprocess.Popen(
        [sys.executable, str(COLAB / "r1_tierb_supervisor.py"), "--batch", "B1",
         "--python", str(fake), "--code-dir", str(tmp_path), "--original", str(tmp_path),
         "--work", str(tmp_path / "work"), "--drive-root", str(drive), "--session", "B1-killed",
         "--start-epoch", str(time.time()), "--budget-hours", "11", "--reserve-minutes", "1",
         "--backup-minutes", "0.005", "--max-workers", "1", "--poll-seconds", "0.2",
         "--provenance", str(provenance)],
        start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    root = tb.batch_root(drive, "B1")
    task = tb.batch_tasks("B1")[0]
    task_dir = root / "checkpoints" / tb.slug(task)
    deadline = time.time() + 60
    while time.time() < deadline and not tb.committed_checkpoints(task_dir):
        time.sleep(0.2)
    os.killpg(process.pid, signal.SIGKILL)                        # the runtime disappears
    process.wait()
    assert not list(root.glob("sessions/*/session_summary.json"))
    ledger = tb.session_ledger(root)
    assert ledger["terminated"] == []
    [killed] = ledger["interrupted"]
    assert killed["session"] == "B1-killed" and killed["state"].startswith("interrupted")
    assert killed["checkpoints"] >= 1 and killed["payloads_committed_by_task"] == {task: 4}
    assert killed["lease_released"] is False and killed["session_dir"]
    _, manifest = tb.committed_checkpoints(task_dir)[0]
    record = manifest["session_record"]                         # traceable from Drive data alone
    assert record["session"] == "B1-killed" and record["orchestration_commit"] == "f" * 40
    assert record["scientific_commit"] == tb.SCIENTIFIC_PIN
    # while its lease is fresh, a second session of the same batch is refused and leaves
    # no session record of its own
    code = None
    try:
        code = supervisor.main(["--batch", "B1", "--python", str(fake), "--code-dir", str(tmp_path),
                                "--original", str(tmp_path), "--work", str(tmp_path / "w2"),
                                "--drive-root", str(drive), "--session", "B1-second",
                                "--start-epoch", str(time.time()), "--budget-hours", "11",
                                "--max-workers", "1"])
    except tb.TierBError as error:
        assert "already active" in str(error)
    assert code is None
    assert [e["session"] for e in tb.session_ledger(root)["interrupted"]] == ["B1-killed"]


def test_a_terminated_session_is_reported_as_terminated(tmp_path):
    import time
    code, summary = _run(tmp_path, "B3", 11.0, time.time())
    ledger = tb.session_ledger(tb.batch_root(tmp_path / "drive", "B3"))
    assert ledger["interrupted"] == []
    assert [e["state"] for e in ledger["terminated"]] == ["terminated: complete"]
    assert ledger["payloads_committed_by_task"] == {t: 4 for t in tb.batch_tasks("B3")}
