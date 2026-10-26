"""Plain-text blocks for the console and the execution log."""

from __future__ import annotations

import time
from typing import Any

from .state import ChainState, RunState, StageState, fmt_duration

RULE = "=" * 78
THIN = "-" * 78


def clock(t: float | None = None) -> str:
    return time.strftime("%H:%M:%S", time.gmtime(t if t is not None else time.time()))


def utc(t: float | None) -> str:
    if t is None:
        return "n/a"
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(t))


def period(date: str, frequency: str) -> str:
    """A date as its period: 2005-04 for monthly, 2017Q2 for quarterly data."""
    if not date or len(date) < 7:
        return date or "-"
    if frequency == "Q":
        return f"{date[:4]}Q{(int(date[5:7]) - 1) // 3 + 1}"
    if frequency == "M":
        return date[:7]
    return date


def _units(stage: StageState) -> str:
    planned = "?" if stage.planned_units is None else str(stage.planned_units)
    return f"{stage.completed_units}/{planned}"


def stage_start(state: RunState, stage: StageState, detail: dict[str, Any]) -> str:
    total = len(state.stages)
    lines = [RULE,
             f"[{clock(stage.started)}] STAGE {stage.number}/{total} START: {stage.name}",
             f"  started        {utc(stage.started)}",
             f"  checkpoint     {stage.checkpoint}   (methodology: {stage.methodology})",
             f"  operations     {stage.operations}"]
    if detail.get("series"):
        lines.append(f"  series         {', '.join(detail['series'])}")
    if detail.get("models"):
        lines.append(f"  models         {', '.join(detail['models'])}")
    if stage.planned_units is not None:
        lines.append(f"  planned tasks  {stage.planned_units} {detail.get('unit', 'tasks')}")
    if detail.get("chains"):
        lines.append(f"  rolling chains {detail['chains']} chains, "
                     f"{detail.get('origins', '?')} forecast origins (model fits)"
                     + (" [provisional]" if detail.get("provisional") else ""))
    lines.append(RULE)
    return "\n".join(lines)


def stage_end(state: RunState, stage: StageState, now: float) -> str:
    total = len(state.stages)
    counts = state.stage_counts()
    status = stage.status.upper()
    lines = [THIN,
             f"[{clock(stage.ended)}] STAGE {stage.number}/{total} {status}: {stage.name}",
             f"  elapsed        {fmt_duration(stage.elapsed(now))}",
             f"  tasks done     {_units(stage)}"]
    chains = [c for c in state.chains.values() if c.plan.stage == stage.key]
    if chains:
        done = sum(c.status == "done" for c in chains)
        skipped = sum(c.status == "skipped" for c in chains)
        failed = sum(c.status == "failed" for c in chains)
        origins = sum(c.completed for c in chains)
        fitted = sum(c.fitted for c in chains)
        cached = sum(c.from_cache for c in chains)
        invalid = sum(c.failed for c in chains)
        records = sum(c.n_records for c in chains)
        lines.append(f"  chains         {done} done, {skipped} skipped, {failed} errored "
                     f"(of {len(chains)})")
        lines.append(f"  origins        {origins} ({fitted} fitted, {cached} from cache); "
                     f"{invalid} failed estimations")
        lines.append(f"  forecast recs  {records}")
    if stage.registry:
        r = stage.registry
        lines.append(f"  registered     {r['failed']} failed estimations, {r['fragile']} "
                     f"fragility flags, {r['data_gaps']} data gaps (failure registry T4.7)")
    for error in stage.errors:
        lines.append(f"  ERROR          {error}")
    lines.append(f"  overall        {counts['done']}/{counts['total']} stages complete; "
                 f"next: {state.next_work()}")
    lines.append(THIN)
    return "\n".join(lines)


def chain_identity(chain: ChainState) -> str:
    p = chain.plan
    regimes = f", K={p.k_regimes}" if p.k_regimes and "K=" not in p.spec_label else ""
    return (f"{p.series} | {p.model} {p.spec_label}{regimes} | window {p.window_length} "
            f"| h={','.join(str(h) for h in p.horizons)}")


def chain_start(state: RunState, chain: ChainState) -> str:
    slot = state.slot_of(chain)
    who = ("main process" if chain.plan.runs_in == "parent" or not slot
           else f"worker {slot}")
    return (f"[{clock(chain.started)}] CHAIN START ({who}) {chain_identity(chain)} "
            f"| {chain.plan.n_origins} origins | {chain.plan.exercise}")


def chain_end(chain: ChainState) -> str:
    mean = chain.mean_fit_seconds()
    took = (chain.ended or 0) - (chain.started or chain.ended or 0)
    return (f"[{clock(chain.ended)}] CHAIN {'DONE' if chain.status == 'done' else chain.status.upper()} "
            f"{chain.plan.series} | {chain.plan.model} | window {chain.plan.window_length} "
            f"| {chain.completed}/{chain.plan.n_origins} origins: {chain.valid} valid, "
            f"{chain.failed} failed, {chain.gaps} data gaps, {chain.from_cache} cached "
            f"| {chain.n_records} forecasts | mean fit "
            f"{'n/a' if mean is None else f'{mean:.2f}s'} | chain {fmt_duration(took)}")


def chain_milestone(chain: ChainState, now: float) -> str:
    mean = chain.mean_fit_seconds()
    pct = 100.0 * chain.completed / max(1, chain.plan.n_origins)
    f = chain.plan.frequency
    return (f"[{clock(now)}]   {chain.plan.series} | {chain.plan.model} "
            f"| window {period(chain.window_start, f)}..{period(chain.window_end, f)} "
            f"| origin {period(chain.current_origin, f)} "
            f"| {chain.completed}/{chain.plan.n_origins} ({pct:.0f}%), "
            f"{chain.plan.n_origins - chain.completed} left | valid {chain.valid}, "
            f"failed {chain.failed} | mean fit {'n/a' if mean is None else f'{mean:.2f}s'} "
            f"| chain {fmt_duration(now - (chain.started or now))}")


def workers(state: RunState, now: float) -> str:
    stage = state.stages.get(state.current_stage or "")
    lines = [f"[{clock(now)}] HEARTBEAT  stage {stage.number if stage else '?'}"
             f"/{len(state.stages)} {stage.name if stage else ''}  "
             f"(run {fmt_duration(now - (state.started or now))})"]
    active = state.active_chains()
    for chain in active:
        slot = state.slot_of(chain)
        f = chain.plan.frequency
        where = "main process" if chain.plan.runs_in == "parent" else f"Worker {slot or '?'}"
        lines.append(f"  {where}: {chain.plan.series} | {chain.plan.model} "
                     f"| origin {period(chain.current_origin, f)} "
                     f"| window {period(chain.window_start, f)}..{period(chain.window_end, f)} "
                     f"| {chain.plan.exercise}")
        if chain.origin_started is not None:
            running = now - chain.origin_started
            detail = f"fit running {fmt_duration(running)}"
            if chain.substep:
                detail += f", active: {chain.substep}"
            lines.append(f"            {detail}")
        mean = chain.mean_fit_seconds()
        lines.append(f"            completed {chain.completed}/{chain.plan.n_origins} origins, "
                     f"{chain.remaining} left; mean fit "
                     f"{'n/a' if mean is None else f'{mean:.2f}s'}; "
                     f"last event {fmt_duration(now - (chain.last_event or now))} ago")
        beat = state.workers_seen.get(chain.pid or -1)
        if beat is not None:
            lines.append(f"            process alive: last heartbeat "
                         f"{fmt_duration(now - beat['t'])} ago, cpu "
                         f"{fmt_duration(beat.get('cpu_seconds'))}, rss "
                         f"{beat.get('rss_mb') or 0:.0f} MB")
    for op in state.active_ops.values():
        lines.append(f"  Operation: {op.category} {op.label} running "
                     f"{fmt_duration(now - op.started)}")
    if stage is not None and stage.unit_label and not active:
        lines.append(f"  Task: {stage.unit_label} (running "
                     f"{fmt_duration(now - (stage.unit_started or now))}), "
                     f"stage tasks {_units(stage)}"
                     + (f", active: {stage.unit_substep}" if stage.unit_substep else ""))
    if state.active_batch is not None:
        ids = state.batches.get(state.active_batch, [])
        statuses = [state.chains[i].status for i in ids]
        lines.append(f"  Batch {state.active_batch}: {statuses.count('done')} done, "
                     f"{statuses.count('active')} active, {statuses.count('queued')} queued "
                     f"of {len(ids)} chains")
    origins = state.origin_counts()
    chains = state.chain_counts()
    lines.append(f"  GLOBAL: chains {chains['done']}/{chains['planned']} done, "
                 f"{chains['active']} active, {chains['queued']} queued; rolling origins "
                 f"(baseline + robustness) {origins['completed']} done, "
                 f"{origins['remaining']} remaining of {origins['planned']}")
    return "\n".join(lines)


def summary(state: RunState, now: float, resources: dict[str, Any]) -> str:
    stage = state.stages.get(state.current_stage or "")
    stages = state.stage_counts()
    chains = state.chain_counts()
    base = state.origin_counts("baseline")
    robust = state.origin_counts("robustness")
    robust_chains = state.chain_counts("robustness")
    lines = [RULE, f"[{clock(now)}] GLOBAL SUMMARY   run {state.run_id}", RULE]
    if stage is not None:
        lines.append(f"  Current stage    {stage.number}/{stages['total']} {stage.name} "
                     f"(running {fmt_duration(stage.elapsed(now))}, tasks {_units(stage)})")
    lines.append(f"  Stages           {stages['done']} complete, {stages['active']} active, "
                 f"{stages['failed']} failed, of {stages['total']}")
    lines.append(f"  Chains           {chains['done']} complete, {chains['active']} active, "
                 f"{chains['queued']} pending, {chains['skipped']} skipped, "
                 f"{chains['failed']} errored, of {chains['planned']} planned"
                 + (f" ({chains['provisional']} provisional)" if chains["provisional"] else ""))
    lines.append(f"  Baseline origins {base['completed']} done, {base['remaining']} remaining "
                 f"of {base['planned']} ({base['fitted']} fitted, {base['from_cache']} cached; "
                 f"{base['forecast_records']} forecast records)")
    lines.append(f"  Robustness       {robust_chains['done']}/{robust_chains['planned']} chains; "
                 f"{robust['completed']} origins done, {robust['remaining']} remaining "
                 f"of {robust['planned']}")
    lines.append(f"  Elapsed          {fmt_duration(now - (state.started or now))}")
    if resources:
        lines.append("  Resources        " + ", ".join(f"{k} {v}" for k, v in resources.items()))
    longest = state.longest_running(now)
    if longest is not None:
        lines.append(f"  Longest running  {longest['what']} ({fmt_duration(longest['seconds'])})")
    if state.last_progress is not None:
        lines.append(f"  Last progress    {fmt_duration(now - state.last_progress)} ago: "
                     f"{state.last_progress_what}")
    if state.last_checkpoint:
        lines.append(f"  Last checkpoint  {state.last_checkpoint['name']} at "
                     f"{utc(state.last_checkpoint['t'])}")
    means = state.mean_fit_seconds()
    if means:
        top = sorted(means.items(), key=lambda kv: -kv[1]["mean_seconds"])[:6]
        lines.append("  Mean fit time    " + "; ".join(
            f"{k} {v['mean_seconds']:.2f}s (n={v['fits']})" for k, v in top))
    if state.operations:
        top = sorted(state.operations.items(), key=lambda kv: -kv[1].seconds)[:6]
        lines.append("  Costliest ops    " + "; ".join(
            f"{k} {fmt_duration(v.seconds)} (n={v.count}, max {v.max_seconds:.1f}s)"
            for k, v in top))
    estimate = state.estimate_remaining()
    if estimate["available"]:
        lines.append(f"  Estimate         UNCERTAIN: at least "
                     f"{fmt_duration(estimate['fit_wall_seconds_lower_bound'])} of wall time "
                     f"({fmt_duration(estimate['fit_cpu_seconds'])} fit CPU) for "
                     f"{estimate['timed_share']:.0%} of the remaining rolling fits; excludes "
                     f"evaluation bootstraps and tables")
        if estimate["untimed"]:
            lines.append("                   not estimated (no timings yet): " + ", ".join(
                f"{k} {v} origins" for k, v in sorted(estimate["untimed"].items())))
        if estimate["provisional_plan"]:
            lines.append("                   plan partly provisional (GARCH/VAR run only "
                         "if their screens pass)")
    else:
        lines.append(f"  Estimate         none yet: {estimate['reason']}")
    lines.append(f"  Next             {state.next_work()}")
    if state.warnings:
        lines.append(f"  Warnings         {len(state.warnings)} (latest: "
                     f"{state.warnings[-1]['message'][:90]})")
    if state.failures:
        lines.append(f"  Failures         {len(state.failures)} (latest: "
                     f"{str(state.failures[-1].get('error', ''))[:90]})")
    lines.append(RULE)
    return "\n".join(lines)
