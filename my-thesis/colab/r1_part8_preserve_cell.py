# Part 8 candidate: PRESERVE cell. Paste into the ORIGINAL integration notebook and run it in the
# runtime of session integration-20261108T052245Z-9bba8e. Read-only on the release tree; writes only a NEW folder
# baseline/r1_part8_candidate_archive/<archive session>/ on Drive. No estimation, no publication.
import os, sys, json, time, secrets, hashlib, importlib, subprocess
from pathlib import Path
ARCHIVE_TOOL_COMMIT = "878d9289986e48bcf40c8ff4e32f22f620cf0937"
ARCHIVE_TOOL_SHA256 = "efc20c988dc7072404b1317d9fe983588dcf8d5f683c558b30efa2615c637c59"
REPOSITORY = globals().get("REPOSITORY", "charlijomedia-dotcom/academia7")
BRANCH = globals().get("BRANCH", "part8-r1-rescore")
WORK = globals().get("WORK", "/content/r1_part8_integration")
DRIVE_ROOT = globals().get("DRIVE_ROOT", "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29")
WRITE_ARCHIVE = True
ORIGINAL_RELEASE = Path(WORK) / "dryrun" / "integration-20261108T052245Z-9bba8e" / "release"
if not ORIGINAL_RELEASE.is_dir():
    print("NOT FOUND:", ORIGINAL_RELEASE, "- the audited tree is gone; use r1_part8_candidate_archive.ipynb.")
else:
    if not Path("/content/drive/MyDrive").exists():
        from google.colab import drive
        drive.mount("/content/drive")
    # The archive tool, fetched read-only from ARCHIVE_TOOL_COMMIT and checked against its pinned sha256.
    TOOL_DIR = Path(WORK) / "archive_tool" / ARCHIVE_TOOL_COMMIT[:12]
    TOOL_DIR.mkdir(parents=True, exist_ok=True)
    _tool_repo = Path(WORK) / "archive_tool" / "repo"
    _env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    if "GIT_ENV" in globals():
        _env = dict(GIT_ENV)
    if not (_tool_repo / ".git").exists():
        subprocess.run(["git", "clone", "--no-checkout", "--filter=blob:none",
                        f"https://github.com/{REPOSITORY}.git", str(_tool_repo)], check=True, env=_env)
    subprocess.run(["git", "fetch", "origin", BRANCH], cwd=_tool_repo, check=True, env=_env)
    _src = subprocess.run(["git", "show", f"{ARCHIVE_TOOL_COMMIT}:my-thesis/colab/r1_integration_archive.py"], cwd=_tool_repo,
                          check=True, capture_output=True, env=_env).stdout
    assert hashlib.sha256(_src).hexdigest() == ARCHIVE_TOOL_SHA256, "archive tool does not match its pinned sha256"
    (TOOL_DIR / "r1_integration_archive.py").write_bytes(_src)
    sys.path.insert(0, str(TOOL_DIR))
    import r1_integration_archive as arc
    importlib.reload(arc)
    AUDITED_EXPORT = Path(DRIVE_ROOT) / "baseline/r1_part8_integration_dryrun/integration-20261108T052245Z-9bba8e"
    arc.verify_audited_export(AUDITED_EXPORT)
    print("archive tool", ARCHIVE_TOOL_COMMIT[:12], "verified; audited export verified:", AUDITED_EXPORT)
    MODE_RESOLVED = "preserve"
    # PRESERVE: exact verification of the audited tree (465 files) against the audited inventory.
    if MODE_RESOLVED == "preserve":
        GATE = arc.preserve_check(ORIGINAL_RELEASE, AUDITED_EXPORT)
        RELEASE_DIR, SOURCE_SESSION, SOURCE_RUN_ID = ORIGINAL_RELEASE, arc.AUDITED_SESSION, arc.AUDITED_RUN_ID
        SOURCE_ORCHESTRATION = arc.AUDITED_ORCHESTRATION
        print("preserve check passed:", GATE["files"], "files, all identical to the audited inventory")
    # Write the archive to a NEW Drive folder (refuses if it exists), then re-read and verify it.
    ARCHIVE_SESSION = f"archive-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}"
    IDENTITY = arc.run_identity(mode=GATE["mode"], archive_session=ARCHIVE_SESSION,
                                archive_tool_commit=ARCHIVE_TOOL_COMMIT,
                                orchestration_commit=SOURCE_ORCHESTRATION, scientific_commit=arc.SCIENTIFIC_PIN,
                                run_id=SOURCE_RUN_ID, source_session=SOURCE_SESSION)
    if not WRITE_ARCHIVE:
        print("WRITE_ARCHIVE is False; gate report:", json.dumps(GATE)[:2000])
    else:
        MANIFEST = arc.write_archive(RELEASE_DIR, DRIVE_ROOT, ARCHIVE_SESSION, IDENTITY, GATE)
        DEST = Path(DRIVE_ROOT) / arc.ARCHIVE_PARENT / ARCHIVE_SESSION
        print(json.dumps(arc.verify_archive(DEST)))
        print(f"archived {MANIFEST['files']} files to {DEST}; release.tar.gz sha256 {MANIFEST['release_tar_sha256']}")
        print("Nothing was published. Please send this folder name to Claude:", ARCHIVE_SESSION)
