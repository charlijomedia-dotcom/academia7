# Reproducing this thesis's empirical results

This repository reproduces its complete empirical pipeline from a frozen dataset using one
Python command. It needs **no FRED API key, no internet connection, and no AI tooling** —
the approved data snapshot is committed, and every result is computed from it.

These instructions are written for a personal **Windows** PC. The macOS and Linux steps are
identical except where noted.

---

## 1. What you need

| | Requirement | Note |
|---|---|---|
| **Python** | 3.11 | The pinned dependency set was resolved for 3.11.15. 3.12+ may resolve differently and is untested. |
| **Git** | any recent version | Used to clone, and to record which commit produced a result. |
| **Disk** | ~2 GB free | Repository ~10 MB; virtual environment ~700 MB; a full run's outputs and fit cache a few hundred MB. |
| **Memory** | 8 GB minimum, 16 GB comfortable | The heaviest step is the three-regime Markov-switching filter over 243 expanded states. |
| **CPU** | 4 cores recommended | The pipeline runs four worker processes by default. Fewer cores work; the run just takes longer. |
| **Time** | minutes to hours | See §5. The reduced-computation check takes about half an hour; the full thesis run takes several hours. |

R is **not** required. It was used once to generate reference values for a statistical
test; those values are stored in the repository and the test reads them from there.

## 2. Install Python

Download Python **3.11** from [python.org/downloads](https://www.python.org/downloads/) and
run the installer. On the first screen tick **"Add python.exe to PATH"**.

Open **PowerShell** and confirm:

```powershell
py -3.11 --version
```

You should see `Python 3.11.x`. If `py` is not recognised, reopen PowerShell, or use the
full path to `python.exe`.

## 3. Get the repository

```powershell
cd $HOME\Documents
git clone https://github.com/charlijomedia-dotcom/academia7.git
cd academia7\my-thesis
```

The frozen dataset arrives with the clone. Nothing is downloaded at run time.

## 4. Create the environment and install the pinned dependencies

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r code\requirements.lock.txt
```

Your prompt should now start with `(.venv)`. Leave it active for everything below.

The `.venv` folder is excluded from version control, so creating it here does not affect
the repository's state or the integrity checks a full run performs.

> **If PowerShell refuses to run the activation script** ("running scripts is disabled on
> this system"), allow signed local scripts for your user once:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> then activate again. Alternatively use `cmd.exe` and `.\.venv\Scripts\activate.bat`.

The versions in `code\requirements.lock.txt` are the exact ones every published result was
produced with. Installing anything else may change numerical output in the last digits.

## 5. Run it

All commands are run from the `my-thesis\code` directory:

```powershell
cd code
```

### 5.1 Check the frozen data (seconds)

```powershell
python run_all.py --data-only
```

This verifies the dataset's hashes, loads it, and stops. It writes nothing. Expect:

```
data store state: complete
canonical input: thesis_input_2026-10-05.csv  sha256=7e7dc769bd63ca49...
rows: 5808
  panel M: 956 periods x 6 series, 1947-01-01 to 2026-08-01
  panel Q: 318 periods x 1 series, 1947-01-01 to 2026-04-01
```

If the hash differs from `7e7dc769bd63ca49`, your copy of the data is not the approved one.
Stop and re-clone rather than continuing.

### 5.2 Reduced-computation run (about 30 minutes)

```powershell
python run_all.py --smoke-test
```

This executes **every stage** of the pipeline on two targets with a short out-of-sample
block. It is the recommended way to confirm your installation works end to end. Its results
are a code-path check, **not** thesis results — see §7.

### 5.3 Full thesis run (several hours)

```powershell
python run_all.py
```

All six targets, the approved estimation windows, every robustness exercise. Leave the
machine on; closing the PowerShell window stops the run.

**The run is resumable.** Fitted models are cached, so if it is interrupted, simply run the
same command again: completed work is reused and the run continues rather than restarting.

## 6. Where the results go

| Directory | Contents |
|---|---|
| `my-thesis\output\` | **Thesis-facing results** from the full run |
| `my-thesis\output\data_audit\` | Data dictionary, imputation audit, LOCF exposure |
| `my-thesis\output\diagnostics\` | Stationarity, nonlinearity, specification tables |
| `my-thesis\output\models\` | In-sample adequacy, nonlinear credibility, fit records |
| `my-thesis\output\forecasts\` | Per-series forecasts and origin audits |
| `my-thesis\output\forecast_tests\` | Accuracy, HLZ, DM-HLN, Model Confidence Set, state tables |
| `my-thesis\output\robustness\` | Every robustness exercise and the failure registry |
| `my-thesis\output\figures\` | All figures, PNG and PDF, each with a provenance sidecar |
| `my-thesis\output\logs\` | Per-stage runtime, environment record, checkpoints |
| `my-thesis\output\manifests\` | Run manifest, output inventory with per-file hashes |
| `my-thesis\smoke_output\` | Reduced-computation results — never thesis-facing |
| `my-thesis\cache\`, `smoke_cache\` | Fitted-model cache; safe to delete, only costs time |
| `my-thesis\run_logs\` | Progress logs of each run (console log, events, snapshot); operational, never thesis-facing |

Every table carries the run ID, data hash, code commit, configuration hash and timestamp,
so any number can be traced back to what produced it.

### 6.1 Watching a long run

While a run is going, the console shows which stage, series, model, window and forecast
origin is being computed, how many origins are done and remain, how long the current fit
has been running, and a global summary every five minutes. The same information is kept
in `run_logs\<namespace>\<run_id>\` as a log, an event stream and a progress snapshot
(`progress.json`). See `MONITORING.md` for how to read them and how remaining work is
counted. On Google Colab, use `colab/run_thesis_colab.ipynb`.

## 7. Telling a check apart from a result

The two never mix, by construction:

- A full run writes to `output\` and its tables carry a run ID beginning **`baseline-`**.
- A reduced run writes to `smoke_output\` and its tables carry a run ID beginning
  **`smoke-`**.

`smoke_output\` is excluded from version control. If a figure or table carries a `smoke-`
run ID, it is a code-path check and must not be quoted as a result.

## 8. Running the test suite (optional, about 30 minutes)

```powershell
python -m pytest -q
```

Expect every test to pass. This exercises the statistical procedures against published
references and independent implementations.

## 9. Troubleshooting

**`DirtyTreeError: the working tree has uncommitted changes outside the run's own output
directories`**
A full run refuses to start if anything that determines the result — code, configuration,
data, specifications — has been modified without being committed. The message names the
files. Either revert them (`git checkout -- <file>`) or commit them. The run's own outputs
and caches never trigger this, so repeated runs are fine.

**`FrozenDataError: the local data store is partial, corrupt or hash-mismatched`**
The dataset does not match its recorded hashes. This is deliberate: the pipeline refuses to
silently re-download or repair. Re-clone the repository.

**The run seems to hang on "forecasting"**
It has not hung. The Markov-switching models are slow, particularly the three-regime
variant. Per-stage progress appears in `output\logs\runtime_log.csv` once the run finishes;
while it runs, Task Manager will show four busy Python processes.

**Out of memory**
Reduce the worker count in `code\configs\baseline.yaml` (`execution.parallel_workers`) from
4 to 2, or run with `--no-cache` removed so cached fits are reused. Lowering the worker
count changes no result — only the speed.

**The run stopped when I closed PowerShell**
Windows terminates child processes with the console. Start the run and leave the window
open, or use `Start-Process` to detach it.

**Figures do not appear / a backend error mentions Tk**
The pipeline writes figures to files and never opens a window, so this should not arise. If
it does, set `MPLBACKEND=Agg` before running:
```powershell
$env:MPLBACKEND = "Agg"
```

**"Filename too long" during clone**
Enable long paths once, in an **Administrator** PowerShell:
```powershell
git config --system core.longpaths true
```
The repository's own paths are well under the limit; this only matters if you clone into an
already-deep folder.

## 10. What not to do

- **Do not delete or edit anything under `data\frozen\`.** It is the approved snapshot and
  its hashes are checked on every run.
- **Do not refresh the data** to make it current. The thesis is deliberately fixed to the
  5 October 2026 vintage. A refresh writes to a separate dated directory and never replaces
  the frozen set.
- **Do not quote numbers from `smoke_output\`.** See §7.
