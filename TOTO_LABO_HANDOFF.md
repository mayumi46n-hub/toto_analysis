# TOTO LABO — HEADQUARTERS HANDOFF

## 2026-10-19 AM checkpoint

### Completed / preserved
- FootyStats safe dry-run/resume hardening is committed and pushed: `8d99ae9`.
- Round1663 FootyStats manifest remains 13 matches / 39 URLs; live acquisition remains 1/39 due CAPTCHA and must not be aggressively retried or bypassed.
- Existing DRAW research was recovered rather than reinvented: 1650 draw structure -> 1653 draw/loss path -> 1656 match-flow -> historical OOF 2020-2025.
- `draw_path_oof_2020_2025_v02.csv`: N=6623; PATH beats CORE overall (LogLoss 0.573610 vs 0.575640; Brier 0.192827 vs 0.193613), and improves both metrics in 5/6 years. 2023 is a tiny regression.

### Critical caveat
- DRAW PATH v02 is NOT production-approved. Its meta layer uses training-row predictions from models fitted on those same training rows, so nested OOF is not strict enough.
- Do not tune against known Round1660 results. Keep P_base unchanged.

### NEXT START POINT
1. Strictify existing DRAW PATH v02 with nested/temporal OOF without changing the hypothesis to fit results.
2. Re-run historical 2020-2025 comparison and year stability.
3. Only if validation survives: Round1660 pseudo-OOF -> Round1663 blind-forward.
4. Do NOT restart DRAW discovery, dictionary source recovery, Football LAB acquisition discovery, or FootyStats URL archaeology.

### Broader roadmap
After DRAW/NON-WIN validation: reconnect predicted XI -> role-aware player/team strength -> simulation; debug 10K, stability 100K, then 250K/500K/1M only after model validity is established. Target remains a stable pre-match workflow toward Round1670.
