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
