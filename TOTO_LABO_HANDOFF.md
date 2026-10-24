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


## 2026-10-24 — DRAW PATH production-P_base compatibility checkpoint

- Critical compatibility finding: strict DRAW PATH v03 was validated around historical core4 probabilities, but production P_base v1-C score probabilities are materially different (same-ID N=3428; mean absolute probability difference 0.04033; max 0.33565; draw correlation 0.4816). Therefore v03 must NOT be attached directly to production v1-C or Round1660.
- Production v1-C historical OOF is available for 2023-2025: N=3428 (2023=1148, 2024=1140, 2025=1140), with each season generated from prior-year meta training only.
- Historical market 1X2 probabilities join to v1-C by jleague_match_id for 3427/3428 rows; only jleague_match_id=45769 (2025-03-01 Tochigi C vs Numazu) is missing.
- Historical FootyStats Over2.5 odds join successfully for 3428/3428 via jleague_match_id -> historical prediction English team/date identity -> raw FootyStats keys. Do not build a new team-name dictionary for this bridge.
- Frozen compatibility-validation population: 2023=1148 initial training base; strict outer tests are 2024=1140 and 2025=1139, total N=2279. Same-date chronological inner OOF design from v03 remains reusable; no Round1660 result tuning is allowed.
- Round1660 PREMATCH market mapping was verified: normalized inverse 1X2 odds reproduce the historical market_p_* definition. Match 6 Kyoto-Machida has missing PREMATCH market/O-U odds and must fail closed; expected strict-applicable set is 12/13. POSTMATCH data is forbidden.
- NEXT START POINT: implement a separate v1-C-specific strict DRAW PATH compatibility OOF using the frozen v03 architecture/hyperparameters and score_p_* as P_base; evaluate 2024-2025 before any Round1660 outcome evaluation. If it survives, freeze and apply without tuning to Round1660, then Round1663.
