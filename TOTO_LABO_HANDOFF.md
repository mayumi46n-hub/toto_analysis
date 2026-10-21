# TOTO LABO — HEADQUARTERS HANDOFF

## 2026-10-22 checkpoint

### DRAW PATH v03 strict
- `scripts/build_draw_path_oof_v03_strict.py` completed strict nested/temporal historical OOF: N=6623, NULL=0, OOF_YEAR_OK=True.
- PATH improves both LogLoss and Brier in all 6/6 years (2020-2025).
- Overall CORE->PATH: LL 0.575876 -> 0.574323; Brier 0.193701 -> 0.193100.
- Date-cluster bootstrap 95% CI remains improvement-side for both metrics.
- Gain concentration remains a caution: dropping the best realized 1% reverses aggregate gain; do not derive post-hoc thresholds from this.

### Lineage / governance
- 2019-2024 CORE predictions have season-level walk-forward evidence; 2025 has OOS temporal evidence.
- `odds_ft_over25` is not result-derived, but historical toto-deadline availability is NOT PROVEN.
- v03 is a promising strict-OOF candidate, NOT unconditional production promotion; P_base remains unchanged.
- 2020-2025 is not a pristine untouched confirmatory holdout because v01/v02 research informed the architecture.
- Do NOT tune against known Round1660 results.

### NEXT START POINT
1. Freeze/commit the strict v03 checkpoint and continuity files.
2. Run Round1660 pseudo-OOF without result-driven tuning.
3. If it survives, evaluate the Round1663 frozen checkpoint.
4. Then reconnect predicted XI -> role-aware player/team strength -> 90-min simulation.
5. Do NOT restart DRAW discovery, dictionary source recovery, Football LAB discovery, or FootyStats URL archaeology unless a concrete defect appears.

### FootyStats blocker preserved
- Round1663 manifest QA remains 13 matches / 39 URLs; acquisition remains 1/39 due CAPTCHA. Do not bypass or aggressively retry.
