"""Check the numbers quoted in the integrated Part 8 report drafts.

Usage: python check_draft_numbers.py REPORT_DIR EVIDENCE_DIR OUT_CSV [MATRIX_FILE]

Each check names a draft file, a text fragment that must appear in it, and
the integrated value (from integrated_numbers.json or the registry json)
that the fragment quotes, rounded as quoted. Read-only; exits 1 on failure.
"""
import csv, json, sys
from pathlib import Path

MF, RF, FR, JR, CL = ("main_findings.md", "robustness_findings.md",
                      "full_empirical_analysis_report.md",
                      "jury_resolution_status.md", "final_claims_allowed.md")
MX = "claim_evidence_matrix_candidate.csv"
H1 = ("T3.3_h1",)
CHECKS = [
    # (file, fragment, json path, quoted value, decimals)
    (MF, "| 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |", H1 + ("UNRATE|AR", "rmse"), 0.551, 3),
    (MF, "| 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |", H1 + ("UNRATE|ARMA", "rmse"), 0.737, 3),
    (MF, "| 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |", H1 + ("UNRATE|MSAR", "rmse"), 0.491, 3),
    (MF, "| 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |", H1 + ("UNRATE|STAR", "rmse"), 0.592, 3),
    (MF, "| 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |", H1 + ("UNRATE|MSAR", "n_valid"), 698, 0),
    (MF, "| — | 0.237 (688) | 0.189 (697) | −0.103 (703) |", H1 + ("UNRATE|ARMA", "oos_r2"), 0.237, 3),
    (MF, "| — | 0.237 (688) | 0.189 (697) | −0.103 (703) |", H1 + ("UNRATE|MSAR", "oos_r2"), 0.189, 3),
    (MF, "| — | 0.237 (688) | 0.189 (697) | −0.103 (703) |", H1 + ("UNRATE|STAR", "oos_r2"), -0.103, 3),
    (MF, "| 0.546 | 0.482 | 0.492 | 0.556 |", ("UNRATE_h1_common_all_four", "AR"), 0.546, 3),
    (MF, "| 0.546 | 0.482 | 0.492 | 0.556 |", ("UNRATE_h1_common_all_four", "ARMA"), 0.482, 3),
    (MF, "| 0.546 | 0.482 | 0.492 | 0.556 |", ("UNRATE_h1_common_all_four", "MSAR"), 0.492, 3),
    (MF, "| 0.546 | 0.482 | 0.492 | 0.556 |", ("UNRATE_h1_common_all_four", "STAR"), 0.556, 3),
    (MF, "RMSE on the 682 dates common to all four models", ("UNRATE_h1_common_all_four", "n"), 682, 0),
    (CL, "| 0.546 | 0.482 | 0.492 | 0.556 |", ("UNRATE_h1_common_all_four", "MSAR"), 0.492, 3),
    (FR, "| UNRATE | 0.551 | 0.737 (0.237; 0.336/0.518) | **0.491** (0.189; 0.367/0.322) | 0.592 (−0.103; 0.587/**0.0015**, AR better) |", H1 + ("UNRATE|ARMA", "hlz_sq_p"), 0.336, 3),
    (FR, "| UNRATE | 0.551 | 0.737 (0.237; 0.336/0.518) | **0.491** (0.189; 0.367/0.322) | 0.592 (−0.103; 0.587/**0.0015**, AR better) |", H1 + ("UNRATE|MSAR", "hlz_abs_p"), 0.322, 3),
    (FR, "| UNRATE | 0.551 | 0.737 (0.237; 0.336/0.518) | **0.491** (0.189; 0.367/0.322) | 0.592 (−0.103; 0.587/**0.0015**, AR better) |", H1 + ("UNRATE|STAR", "hlz_abs_p"), 0.0015, 4),
    (MF, "| UNRATE MSAR | 0.189 | −0.010 |", ("A3_UNRATE_h1_integrated", "MSAR", "oos_r2_excl_2020_01_2021_06"), -0.010, 3),
    (MF, "| UNRATE ARMA | 0.237 | −0.051 |", ("A3_UNRATE_h1_integrated", "ARMA", "oos_r2_excl_2020_01_2021_06"), -0.051, 3),
    (MF, "χ²(3) = 8.65", ("UNRATE_ARMA_AR_h1_wald", "joint_stat"), 8.65, 2),
    (MF, "p = 0.034", ("UNRATE_ARMA_AR_h1_wald", "joint_p"), 0.034, 3),
    (MF, "χ²(2) = 2.53", ("UNRATE_ARMA_AR_h1_wald", "slopes_stat"), 2.53, 2),
    (MF, "p = 0.282", ("UNRATE_ARMA_AR_h1_wald", "slopes_p"), 0.282, 3),
    (MF, "α = −0.084, p = 0.224", ("UNRATE_ARMA_AR_h1_wald", "alpha"), -0.084, 3),
    (MF, "β_rec = 0.091, p = 0.117", ("UNRATE_ARMA_AR_h1_wald", "beta_rec_p"), 0.117, 3),
    (MF, "β_turn = 0.0002, p = 0.998", ("UNRATE_ARMA_AR_h1_wald", "beta_turn_p"), 0.998, 3),
    (MF, "n = 688)", ("UNRATE_ARMA_AR_h1_wald", "n"), 688, 0),
    (FR, "with 84 recession and 104 turning-window observations", ("UNRATE_ARMA_AR_h1_wald", "n_recession"), 84, 0),
    (FR, "with 84 recession and 104 turning-window observations", ("UNRATE_ARMA_AR_h1_wald", "n_turning_window"), 104, 0),
    (MF, "435 FAILED", ("FR_status_total", "failed"), 435, 0),
    (MF, "23,002 FRAGILE", ("FR_status_total", "fragile"), 23002, 0),
    (MF, "43,816 adequate", ("FR_status_total", "adequate"), 43816, 0),
    (MF, "67,253 fits", ("FR_rows",), 67253, 0),
    (MF, "10,246 fragile of 15,443 fits (adequate 5,128; failed 69)", ("FR_status_by_model", "MSAR", "fragile"), 10246, 0),
    (MF, "10,246 fragile of 15,443 fits (adequate 5,128; failed 69)", ("FR_status_by_model", "MSAR", "adequate"), 5128, 0),
    (MF, "10,246 fragile of 15,443 fits (adequate 5,128; failed 69)", ("FR_status_by_model", "MSAR", "failed"), 69, 0),
    (MF, "29 fits, all UNRATE or FEDFUNDS", ("baseline_failed_fits_h1_total",), 29, 0),
    (MF, "UNRATE AR 1, ARMA 15, MSAR 6; FEDFUNDS ARMA 7", ("baseline_failed_fits_h1", "UNRATE|MSAR"), 6, 0),
    (FR, "| FEDFUNDS MSAR | 49 |", ("FR_failed_by_series_model", "FEDFUNDS|MSAR"), 49, 0),
    (FR, "| UNRATE MSAR | 20 |", ("FR_failed_by_series_model", "UNRATE|MSAR"), 20, 0),
    (FR, "19 of 226 available HLZ tests reject", ("T3.3A_rejections", "reject"), 19, 0),
    (FR, "19 of 226 available HLZ tests reject", ("T3.3A_rejections", "available"), 226, 0),
    (FR, "12 of 230 comparisons disagree", ("T3.3B_disagreements",), 12, 0),
    (FR, "50 of 88 available STAR-pair p-values", ("A4_star_clustering", "in_[0.30,0.34]"), 50, 0),
    (MF, "all 92 cells available", ("T3.4_cells_all",), 92, 0),
    (MF, "all 92 cells available", ("T3.4_unavailable_cells_all",), 0, 0),
    (MF, "the 68 placeholder", None, None, None),  # replaced below
    (RF, "| UNRATE, differences (alt) | **0.563** | 0.680 (0.419) | 0.776 (0.330) | 20.75 (−0.202) |", ("T4.1", "UNRATE|difference|alternative|AR", "rmse"), 0.563, 3),
    (RF, "| UNRATE, differences (alt) | **0.563** | 0.680 (0.419) | 0.776 (0.330) | 20.75 (−0.202) |", ("T4.1", "UNRATE|difference|alternative|MSAR", "oos_r2"), 0.330, 3),
    (RF, "| UNRATE, differences (alt) | **0.563** | 0.680 (0.419) | 0.776 (0.330) | 20.75 (−0.202) |", ("T4.1", "UNRATE|difference|alternative|STAR", "rmse"), 20.75, 2),
    (RF, "| UNRATE, differences (alt) | **0.563** | 0.680 (0.419) | 0.776 (0.330) | 20.75 (−0.202) |", ("T4.1", "UNRATE|difference|alternative|STAR", "oos_r2"), -0.202, 3),
    (RF, "| FEDFUNDS, levels (alt) | **0.426** (n=555) | 0.520 (0.003, n=550) | 0.456 (−0.307; 577 valid, 540 matched) | 0.974 (−4.180) |", ("T4.1", "FEDFUNDS|level|alternative|AR", "rmse"), 0.426, 3),
    (RF, "| FEDFUNDS, levels (alt) | **0.426** (n=555) | 0.520 (0.003, n=550) | 0.456 (−0.307; 577 valid, 540 matched) | 0.974 (−4.180) |", ("T4.1", "FEDFUNDS|level|alternative|MSAR", "rmse"), 0.456, 3),
    (RF, "| FEDFUNDS, levels (alt) | **0.426** (n=555) | 0.520 (0.003, n=550) | 0.456 (−0.307; 577 valid, 540 matched) | 0.974 (−4.180) |", ("T4.1", "FEDFUNDS|level|alternative|MSAR", "oos_r2"), -0.307, 3),
    (RF, "| FEDFUNDS, levels (alt) | **0.426** (n=555) | 0.520 (0.003, n=550) | 0.456 (−0.307; 577 valid, 540 matched) | 0.974 (−4.180) |", ("T4.1", "FEDFUNDS|level|alternative|STAR", "oos_r2"), -4.180, 3),
    (RF, "| FEDFUNDS, levels (alt) | **0.426** (n=555) | 0.520 (0.003, n=550) | 0.456 (−0.307; 577 valid, 540 matched) | 0.974 (−4.180) |", ("T4.1", "FEDFUNDS|level|alternative|MSAR", "n_failed"), 49, 0),
    (RF, "| 3 | 2.958 | 2.072 | 0.075 | 0.101 / **0.013** | 0.012 / 0.0003 |", ("T4.2", "AR(p=3)", "rmse"), 2.958, 3),
    (RF, "| 3 | 2.958 | 2.072 | 0.075 | 0.101 / **0.013** | 0.012 / 0.0003 |", ("T4.2P", "AR(p=3)|absolute", "hlz_p"), 0.013, 3),
    (RF, "| 3 | 2.958 | 2.072 | 0.075 | 0.101 / **0.013** | 0.012 / 0.0003 |", ("T4.2P", "AR(p=3)|absolute", "dm_p"), 0.0003, 4),
    (RF, "| 6 | 2.969 | 2.093 | 0.068 | 0.257 / 0.100 | 0.104 / 0.014 |", ("T4.2P", "AR(p=6)|squared", "hlz_p"), 0.257, 3),
    (RF, "| 12 | 2.967 | 2.080 | 0.069 | 0.327 / 0.101 | 0.180 / 0.019 |", ("T4.2", "AR(p=12)", "oos_r2"), 0.069, 3),
    (RF, "| 12 | 2.967 | 2.080 | 0.069 | 0.327 / 0.101 | 0.180 / 0.019 |", ("T4.2P", "AR(p=12)|absolute", "dm_p"), 0.019, 3),
    (RF, "| 1 | 3.075 | 2.194 | — | — | — |", ("T4.2", "AR(p=1)", "rmse"), 3.075, 3),
    (RF, "use 714 common dates", ("T4.2", "AR(p=1)", "common_dates"), 714, 0),
    (RF, "11 of 138 tests (T4.4P)", ("T4.4P", "hlz_reject"), 11, 0),
    (RF, "| UNRATE | 0.493 | 0.613 | 0.353 | 1 (descriptive) |", ("T4.5C_VAR", "UNRATE", "rmse"), 0.493, 3),
    (RF, "| UNRATE | 0.493 | 0.613 | 0.353 | 1 (descriptive) |", ("T4.5C_AR", "UNRATE"), 0.613, 3),
    (RF, "| UNRATE | 0.493 | 0.613 | 0.353 | 1 (descriptive) |", ("T4.5C_VAR", "UNRATE", "oos_r2"), 0.353, 3),
    (RF, "544 dates (527 for UNRATE", ("T4.5C_VAR", "UNRATE", "common_dates"), 527, 0),
    (RF, "ARMA 0.538, MSAR 0.550", ("T4.5C_UNRATE", "MSAR", "rmse"), 0.550, 3),
    (RF, "| UNRATE MSAR | 0.240 | 0.190 | −1.102 |", ("T4.8C_h1_oos_r2", "UNRATE|MSAR|180"), 0.240, 3),
    (RF, "| UNRATE MSAR | 0.240 | 0.190 | −1.102 |", ("T4.8C_h1_oos_r2", "UNRATE|MSAR|300"), -1.102, 3),
    (RF, "| UNRATE ARMA | 0.302 | 0.238 | 0.202 |", ("T4.8C_h1_oos_r2", "UNRATE|ARMA|240"), 0.238, 3),
    (RF, "| UNRATE STAR | −2.714 | −0.104 | −0.075 |", ("T4.8C_h1_oos_r2", "UNRATE|STAR|180"), -2.714, 3),
    (RF, "where it ranks 4th of 4 by RMSE and AR ranks 1st", ("T4.8C_h1_rank_rmse_UNRATE", "MSAR|300"), 4, 0),
    (RF, "where it ranks 4th of 4 by RMSE and AR ranks 1st", ("T4.8C_h1_rank_rmse_UNRATE", "AR|300"), 1, 0),
    (RF, "support absent in both 87, no change 18, strengthened 2, support lost 1", ("T4.8P", "support_change", "support_absent_in_both"), 87, 0),
    (RF, "support absent in both 87, no change 18, strengthened 2, support lost 1", ("T4.8P", "support_change", "no_change"), 18, 0),
    (RF, "all 288 rows (72 cells) are available", ("T4.8M", "cells"), 72, 0),
    (RF, "| UNRATE MSAR OOS R² | 0.191 | 0.189 |", ("T4.9", "UNRATE|MSAR|pre_gap_unaffected", "oos_r2"), 0.191, 3),
    (RF, "TP1 has 552 rows", ("TP1", "rows"), 552, 0),
    (RF, "174 unchanged, 24 reversed (sign flips of insignificant differentials), 3 weakened, 6 unavailable", ("TP1", "conclusion_vs_baseline", "reversed"), 24, 0),
    (RF, "174 unchanged, 24 reversed (sign flips of insignificant differentials), 3 weakened, 6 unavailable", ("TP1", "conclusion_vs_baseline", "unchanged"), 174, 0),
    (FR, "AR RMSE is 0.942, 1.165 and 1.492 at h=3, 6 and 12", ("T3.3_UNRATE_multistep", "h12|AR", "rmse"), 1.492, 3),
    (FR, "MSAR's OOS R² is negative at h=3, 6 and 12 (−0.129, −0.538, −0.952)", ("T3.3_UNRATE_multistep", "h12|MSAR", "oos_r2"), -0.952, 3),
    (FR, "ARMA's is 0.056, −0.137 and 0.093", ("T3.3_UNRATE_multistep", "h6|ARMA", "oos_r2"), -0.137, 3),
    (FR, "- **512 FAILED-category events.**", ("REG", "by_category", "failed"), 512, 0),
    (FR, "- **33,610 FRAGILE-category events:**", ("REG", "by_category", "fragile"), 33610, 0),
    (FR, "  - NONCONVERGENCE: 329;", ("REG", "by_category_reason", "failed|NONCONVERGENCE"), 329, 0),
    (FR, "  - SINGULAR_COV: 47, attached", ("REG", "by_category_reason", "failed|SINGULAR_COV"), 47, 0),
    (FR, "  - LOW_OCCUPANCY: 8,835;", ("REG", "by_category_reason", "fragile|LOW_OCCUPANCY"), 8835, 0),
    (FR, "  - ILL_CONDITIONED_COV: 5,941;", ("REG", "by_category_reason", "fragile|ILL_CONDITIONED_COV"), 5941, 0),
    (FR, "  - SINGULAR_COV: 4,062;", ("REG", "by_category_reason", "fragile|SINGULAR_COV"), 4062, 0),
    (FR, "  - TRANSITION_BOUNDARY: 3,845;", ("REG", "by_category_reason", "fragile|TRANSITION_BOUNDARY"), 3845, 0),
    (FR, "### C.1 The 34,122 failure-registry events (T4.7)", ("REG", "rows"), 34122, 0),
    (JR, "initial window statistic −4.556, p = 0.189", ("ZA", 0, "p_value"), 0.189, 3),
    (JR, "full sample −4.606, p = 0.169", ("ZA", 1, "statistic"), -4.606, 3),
    (JR, "initial window −3.500, p = 0.811", ("ZA", 2, "p_value"), 0.811, 3),
    (JR, "full sample −4.290, p = 0.320", ("ZA", 3, "statistic"), -4.290, 3),
    (JR, "it has the lowest RMSE (0.493 against AR 0.613)", ("T4.5C_VAR", "UNRATE", "rmse"), 0.493, 3),
    (CL, "| 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |", H1 + ("UNRATE|ARMA", "n_valid"), 689, 0),
    (CL, "10,246 of 15,443 MSAR fits", ("FR_status_by_model", "MSAR", "fragile"), 10246, 0),
    (CL, "UNRATE MSAR h=1 OOS R² 0.240, 0.190 and −1.102", ("T4.8C_h1_oos_r2", "UNRATE|MSAR|240"), 0.190, 3),
    (CL, "for ARMA (in ARMA's favour, p = 0.0076)", ("T4.1P_parsed", "FEDFUNDS ARMA level absolute", "dm"), 0.0076, 4),
    (CL, "and for MSAR (against MSAR, p = 0.029)", ("T4.1P_parsed", "FEDFUNDS MSAR level absolute", "dm"), 0.029, 3),
    (CL, "HLZ governs (p = 0.146 and 0.145)", ("T4.1P_parsed", "FEDFUNDS MSAR level absolute", "hlz"), 0.145, 3),
    # C16 (revised 9 November 2026)
    (RF, "AR(2) has RMSE 2.966 and MAE 2.084 [audit], against 2.967 and 2.080 for AR(12)", ("C16", "AR2_on_714", "rmse"), 2.966, 3),
    (RF, "AR(2) has RMSE 2.966 and MAE 2.084 [audit], against 2.967 and 2.080 for AR(12)", ("C16", "AR2_on_714", "mae"), 2.084, 3),
    (RF, "AR(2) has RMSE 2.966 and MAE 2.084 [audit], against 2.967 and 2.080 for AR(12)", ("T4.2", "AR(p=12)", "rmse"), 2.967, 3),
    (RF, "AR(2) has RMSE 2.966 and MAE 2.084 [audit], against 2.967 and 2.080 for AR(12)", ("T4.2", "AR(p=12)", "mae"), 2.080, 3),
    (RF, "AR(12) does not significantly beat AR(1) (HLZ p = 0.327 squared, 0.101 absolute)", ("T4.2P", "AR(p=12)|squared", "hlz_p"), 0.327, 3),
    (RF, "AR(12) does not significantly beat AR(1) (HLZ p = 0.327 squared, 0.101 absolute)", ("T4.2P", "AR(p=12)|absolute", "hlz_p"), 0.101, 3),
    (RF, "the baseline p=2 (2.967 on its own 715 dates)", ("C16", "AR2_own_715", "rmse"), 2.967, 3),
    (CL, "AR(2) has RMSE 2.966 but MAE 2.084, against AR(12)'s 2.967 and 2.080. This is an **[audit] sensitivity**", ("C16", "AR2_on_714", "mae"), 2.084, 3),
    (CL, "2.967 for AR(12) on the 714 common dates; 2.967 for AR(2) on its own 715 dates", ("C16", "AR2_own_715", "rmse"), 2.967, 3),
    (MF, "AR(12) does not significantly beat AR(1) (HLZ p = 0.327 / 0.101)", ("T4.2P", "AR(p=12)|absolute", "hlz_p"), 0.101, 3),
    (FR, "2.966 on the 714 dates [audit]", ("C16", "AR2_on_714", "rmse"), 2.966, 3),
    (FR, "counted 34,122 rows (512 failed, 33,610 fragile)", ("REG", "rows"), 34122, 0),
    (MF, "512 FAILED (including 105 `UNSTABLE_AR`) and 33,610 FRAGILE (T4.7). These totals are verified on the archived", ("REG", "by_category_reason", "failed|UNSTABLE_AR"), 105, 0),
    # candidate claim matrix
    (MX, "AR(2) RMSE 2.966 / MAE 2.084 vs AR(12) 2.967 / 2.080 [audit sensitivity", ("C16", "AR2_on_714", "rmse"), 2.966, 3),
    (MX, "MSAR 10,246 fragile of 15,443 (5,128 adequate, 69 failed)", ("FR_status_by_model", "MSAR", "fragile"), 10246, 0),
    (MX, "34,122 events (512 failed, 33,610 fragile", ("REG", "by_category", "fragile"), 33610, 0),
    (MX, "RMSE on the 682 dates common to all four AR 0.546, ARMA 0.482, MSAR 0.492, STAR 0.556", ("UNRATE_h1_common_all_four", "ARMA"), 0.482, 3),
    (MX, "OOS R2 vs AR on AR-matched samples ARMA 0.237 (688), MSAR 0.189 (697)", H1 + ("UNRATE|MSAR", "oos_r2"), 0.189, 3),
    (MX, "OOS R2 0.240 / 0.190 / -1.102", ("T4.8C_h1_oos_r2", "UNRATE|MSAR|300"), -1.102, 3),
    (MX, "chi2(3) 8.65, p 0.034", ("UNRATE_ARMA_AR_h1_wald", "joint_p"), 0.034, 3),
    (MX, "chi2(2) 2.53, p 0.282", ("UNRATE_ARMA_AR_h1_wald", "slopes_p"), 0.282, 3),
    (MX, "UNRATE differences 0.563; FEDFUNDS levels 0.426", ("T4.1", "FEDFUNDS|level|alternative|AR", "rmse"), 0.426, 3),
    (MX, "only p=3 beats p=1 under HLZ (absolute, p 0.013)", ("T4.2P", "AR(p=3)|absolute", "hlz_p"), 0.013, 3),
]
CHECKS = [c for c in CHECKS if c[2] is not None]


def lookup(data, path):
    obj = data
    for key in path:
        obj = obj[key]
    return obj


def main(drafts, evidence, out_csv):
    drafts, evidence = Path(drafts), Path(evidence)
    data = json.loads((evidence / "integrated_numbers.json").read_text())
    data["REG"] = json.loads((evidence / "registry_reason_codes_local_rehearsal.json").read_text())
    data["C16"] = json.loads((evidence / "c16_ar2_common_sample_audit.json").read_text())
    data["ZA"] = [{"p_value": z["p_value"], "statistic": z["statistic"]}
                  for z in data["T2.2_zivot_andrews"]]
    parsed = {}
    for row in data["T4.1P"]:
        head, rest = row.split(":", 1)
        hlz = float(rest.split("HLZ p=")[1].split(" ")[0])
        dm = float(rest.split("DM-HLN p=")[1].split(" ")[0])
        parsed[head.strip()] = {"hlz": hlz, "dm": dm}
    data["T4.1P_parsed"] = parsed
    texts = {f: (drafts / f).read_text() for f in {c[0] for c in CHECKS}}
    rows, bad = [], 0
    for f, frag, path, quoted, dec in CHECKS:
        present = frag in texts[f]
        try:
            value = lookup(data, path)
            match = value is not None and round(float(value), dec) == round(float(quoted), dec)
        except (KeyError, IndexError, TypeError):
            value, match = None, False
        ok = present and match
        bad += not ok
        rows.append({"draft": f, "fragment": frag, "source": "/".join(map(str, path)),
                     "quoted": quoted, "integrated_value": value,
                     "fragment_present": present, "value_matches": match, "ok": ok})
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} checks, {bad} failed")
    for r in rows:
        if not r["ok"]:
            print("FAIL", r["draft"], r["source"], r["quoted"], r["integrated_value"], r["fragment_present"])
    return 1 if bad else 0


if __name__ == "__main__":
    # optional 4th argument: the claim-matrix file name (the final directory's differs)
    if len(sys.argv) > 4:
        CHECKS = [(sys.argv[4] if c[0] == MX else c[0], *c[1:]) for c in CHECKS]
    sys.exit(main(*sys.argv[1:4]))
