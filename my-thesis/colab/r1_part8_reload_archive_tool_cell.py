# Part 8 candidate archive: RELOAD the corrected archive tool in the EXISTING runtime.
# Paste as a new cell in r1_part8_candidate_archive.ipynb, below section 4f, and run it once.
# It does not re-run the reconstruction, any model or any earlier cell. It reads nothing but the tool
# (git show of one file at the pinned commit) and the audited export, and writes nothing to Drive.
import sys, hashlib, importlib, subprocess
from pathlib import Path
ARCHIVE_TOOL_COMMIT = "878d9289986e48bcf40c8ff4e32f22f620cf0937"
ARCHIVE_TOOL_SHA256 = "efc20c988dc7072404b1317d9fe983588dcf8d5f683c558b30efa2615c637c59"
assert MODE_RESOLVED == "reconstruct" and DRY_EXIT is not None and (DRYRUN / "release").is_dir(), \
    "the reconstructed candidate is not in this runtime; stop"
_repo = Path(WORK) / "archive_tool" / "repo"
_env = dict(GIT_ENV) if "GIT_ENV" in globals() else None
subprocess.run(["git", "fetch", "origin", BRANCH], cwd=_repo, check=True, env=_env)
_src = subprocess.run(["git", "show", f"{ARCHIVE_TOOL_COMMIT}:my-thesis/colab/r1_integration_archive.py"],
                      cwd=_repo, check=True, capture_output=True, env=_env).stdout
assert hashlib.sha256(_src).hexdigest() == ARCHIVE_TOOL_SHA256, "archive tool does not match its pinned sha256"
TOOL_DIR = Path(WORK) / "archive_tool" / ARCHIVE_TOOL_COMMIT[:12]
TOOL_DIR.mkdir(parents=True, exist_ok=True)
(TOOL_DIR / "r1_integration_archive.py").write_bytes(_src)
sys.modules.pop("r1_integration_archive", None)          # drop the old version
sys.path.insert(0, str(TOOL_DIR))
import r1_integration_archive as arc
assert Path(arc.__file__).resolve() == (TOOL_DIR / "r1_integration_archive.py").resolve()
assert hashlib.sha256(Path(arc.__file__).read_bytes()).hexdigest() == ARCHIVE_TOOL_SHA256
assert arc.AUDITED_LEGACY_RUN_ID == "correction-20261108T053006-949fcd76"
arc.verify_audited_export(AUDITED_EXPORT)
print("archive tool", ARCHIVE_TOOL_COMMIT[:12], "loaded from", arc.__file__, "; audited export verified")
print("Now re-run ONLY section 4f (the equivalence gate). Review its output before section 5.")
