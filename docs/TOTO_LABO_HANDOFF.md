# TOTO LABO — CHAT HANDOFF

Updated: 2026-10-04

## 1. START HERE

This file is the short entry point for a new ChatGPT conversation.

Canonical detailed project state:

`TOTO_LABO_STATE.md`

The root STATE is the single canonical research state.

`docs/TOTO_LABO_STATE.md` is LEGACY / historical reference only.
Do not treat it as the current STATE.

Before starting new research:
1. read this HANDOFF
2. read the relevant sections of `TOTO_LABO_STATE.md`
3. inspect existing canonical scripts/artifacts
4. continue from the validated stopping point

Do NOT restart already completed research merely because the chat changed.

---

## 2. PROJECT GOAL

Build a reproducible long-term TOTO LABO that improves toto prediction quality through:

- complete semantic understanding of available data
- temporal / OOF validation
- reproducible acquisition
- player/team/context modeling
- DRAW-path research
- auditable simulation
- disciplined production promotion

Do not optimize only for one round.

No high-prize or profit outcome is guaranteed.

---

## 3. ROUND STRATEGY

### Round 1658
Development / semantic-understanding / parser / dictionary / simulator research round.

Known results must not be used to fit features or coefficients and then presented as predictive validation.

Post-result use is diagnostic only.

### Round 1659
Blind rehearsal target.

Freeze PRE-MATCH data before using results.

Run acquisition -> semantic normalization -> model/simulation -> frozen prediction first.

Reveal results only afterward for evaluation.

### Round 1660
Important prediction target.

Use only mechanisms justified by prior validation.

Do not rush unvalidated research into production merely because Round1660 is approaching.

---

## 4. NON-NEGOTIABLE MODEL GOVERNANCE

`P_base` is the production anchor.

Research layers must NOT silently mutate P_base.

Usage states:

`USED_PBASE`
`USED_WARNING`
`USED_ALLOCATION_REVIEW`
`USED_DATA_QUALITY`
`RESEARCH_ONLY`
`BLOCKED_BY_OOF`
`BLOCKED_BY_MISSING`

Knowledge states:

`CONFIRMED`
`OOF_VALIDATED`
`REJECTED`
`RESEARCH_ONLY`
`UNRESOLVED`

Do not count correlated metrics as independent votes.

Do not force DRAW probability upward.

Do not promote a single-round observation into a production rule.

Do not use post-hoc outcome fitting as forward predictive evidence.

---

## 5. COMPLETE DATA-DICTIONARY PROJECT

Primary sources:

- FootyStats
- Football LAB
- totoONE

Acquisition alone is NOT understanding.

Required progression:

`ACQUIRED`
-> `PARSED`
-> `SEMANTICALLY UNDERSTOOD`
-> `POPULATION DEFINED`
-> `CORRELATION / OVERLAP AUDITED`
-> `MATCH-GENERATION ROLE ASSIGNED`
-> `TEMPORALLY VALIDATED`
-> `ELIGIBLE FOR MODEL USE`

Common dictionary hierarchy:

`SOURCE`
-> `PAGE/FAMILY`
-> `BLOCK/TAB`
-> `METRIC`
-> `POPULATION`
-> `HOME/AWAY CONDITION`
-> `TIME WINDOW`
-> `UNIT`
-> `MEASURED/DERIVED`
-> `MATCH-GENERATION ROLE`
-> `CORRELATION GROUP`
-> `DRAW RELATION`
-> `MISSING SEMANTICS`
-> `OOF STATUS`
-> `USAGE STATUS`

Match-generation map:

`scoring intensity`
-> `chance generation`
-> `attacking route`
-> `shot arrival`
-> `shot quality / xG`
-> `conversion`
-> `set pieces`
-> `timing`
-> `score state`
-> `DRAW path`

FootyStats / Football LAB / totoONE are not three independent prediction votes.

Equivalent or causally adjacent metrics must be checked for double counting.

---

## 6. FOOTYSTATS CURRENT CANONICAL ASSETS

Important current scripts include:

`scripts/fetch_footystats_round_3html_v02.py`

`scripts/parse_footystats_round_full_v02.py`

`scripts/normalize_footystats_round_v05.py`

`scripts/build_footystats_feature_semantic_v04.py`

`scripts/build_score_model_v1c_round_v01.py`

`scripts/reconstruct_v1c_full_pbase_oof_v01.py`

Round1658:
- 39/39 HOME/H2H/AWAY HTML acquired
- 13 parsed match JSON
- normalized 13x65 available
- core xG/xGA data present

FootyStats research/process information must not automatically override P_base.

---

## 7. FOOTBALL LAB CURRENT STATE

Football LAB is a major data source, not merely a CBP auxiliary source.

2026 semantic team population:
- J1 20
- J2 20
- J3 20
- total 60

Validated slug registry:

`data/analysis/football_lab_team_slug_map_2026_v02.csv`

Coverage:
60/60 teams resolved with unique slugs.

Important existing scripts include:

`scripts/fetch_football_lab_cbp_leagues_v02.py`

`scripts/normalize_football_lab_team_cbp_v01.py`

`scripts/fetch_football_lab_toto1654_previews_v01.py`

Current non-CBP full-data expansion remains RESEARCH_ONLY.

Validated / observed Football LAB families include:

`preview`
`formation`
`style`
`transfer`
`season`
`simulation`
`match`
`report`

League summary families include:

`cbp_ranking`
`team_ranking`
`team_style`
`player_ranking`
`player_parameter`
`best11`
`record`

Do NOT interpret URL discovery or slug resolution as semantic understanding.

A generic safe/resumable full-data acquisition layer still needs to be completed.

---

## 8. TOTOONE CURRENT STATE

Current reusable acquisition script:

`scripts/fetch_totoone_lineups_v1.py`

Historical asset:

`scripts/fetch_totoone_historical_lineups_v1.py`

Round1658 predicted-XI data has been acquired.

Predicted XI is primarily:

- player input
- availability input
- role/context input

It is NOT automatically an independent 1X2 vote.

Player utility coefficients require historical validation.

---

## 9. DRAW PRINCIPLE

Research principle:

`引き分けを制するものはtotoを制する`

This is NOT a forced-DRAW rule.

Required generative DRAW paths include:

- 0-0
- 1-1
- 2-2+
- home lead -> away equalizer
- away lead -> home equalizer
- late equalizer
- HT 0-0 -> FT DRAW

Existing DRAW research in `src/analysis`, `src/ml`, `scripts/`, and STATE must be reviewed before creating duplicate research.

---

## 10. SIMULATION

Validation progression:

`10K logic check`
-> `100K stability`
-> `historical temporal OOF`
-> `1M precision run`

One million repetitions are not model validation by themselves.

Future TOTO LABO CONTROL ROOM should show real calculations:

- real simulation progress
- 13-match H/D/A convergence
- checkpoint convergence
- DRAW paths
- P_base vs P_sim
- Monte Carlo uncertainty / stability
- run ID
- random seed
- input snapshot identity
- model version

UI must not alter model logic.

---

## 11. FUTURE ONE-ACTION ROUND PREPARATION

Target interface:

`python scripts/prepare_toto_round.py --round <ROUND>`

Conceptual flow:

`toto official`
-> `J.League safe refresh`
-> `FootyStats URL resolution`
-> `FootyStats 39-page safe acquisition`
-> `FootyStats parse/semantic normalize`
-> `Football LAB full relevant acquisition`
-> `Football LAB semantic normalize`
-> `FootyStats x Football LAB semantic comparison`
-> `totoONE predicted XI`
-> `availability/context`
-> `QA`
-> `simulation readiness`

Acquisition must be polite, resumable, idempotent, and stop safely on 429/bot/invalid responses.

No rate-limit bypass.

---

## 12. GIT GOVERNANCE

Repository has substantial historical material and a dirty working tree.

Never use:

`git add .`

`git reset`

`git clean`

blind `git pull`

Use explicit staging only.

Git should preserve:

- canonical STATE
- HANDOFF
- architecture
- dictionary specifications
- semantic schemas
- validated canonical scripts
- lightweight configs
- QA/provenance rules

Do not blindly commit:

- raw HTML collections
- DB backups
- WAL/SHM
- zip archives
- huge generated datasets
- simulation output
- swap/temp files

Current `scripts/` contains substantial research code that was not Git-tracked at the 2026-10-04 audit.

Classify scripts as:

`CANONICAL`
`HISTORICAL_REFERENCE`
`GENERATED`
`UNRESOLVED`

before selective Git staging.

---

## 13. CURRENT STOPPING POINT

Completed:

- canonical STATE identified as root `TOTO_LABO_STATE.md`
- legacy `docs/TOTO_LABO_STATE.md` distinguished
- 2026 Football LAB 60-team slug registry completed
- current Git state audited
- current scripts inventory audited
- 1658/1659/1660 research strategy appended to canonical STATE

Current Git facts:
- branch: `main`
- remote: `origin`
- current HEAD was aligned with `origin/main` at audit time
- current research artifacts are not yet comprehensively Git-tracked
- bulk staging is prohibited

## NEXT ACTION

After this HANDOFF file is created:

1. verify HANDOFF
2. define first selective Git baseline
3. create common multisource dictionary schema
4. continue FootyStats / Football LAB / totoONE semantic dictionary work
5. prepare Round1659 blind PRE-MATCH acquisition

Do not start unrelated exploratory research before checking STATE.


---

## 14. PROJECT MEMORY / ANTI-REDISCOVERY

Before broad filesystem searches, use the project-memory indexes:

`docs/TOTO_LABO_RESEARCH_INDEX_V2.csv`

`docs/TOTO_LABO_STATE_ASSET_LINKS.csv`

`docs/TOTO_LABO_ASSET_INVENTORY.csv`

Recovery order:

`HANDOFF`
-> `RESEARCH_INDEX_V2`
-> relevant canonical `TOTO_LABO_STATE.md` sections
-> `STATE_ASSET_LINKS`
-> `ASSET_INVENTORY`
-> exact artifact

Do not broadly grep/find the repository merely to rediscover work already recorded here.

Important:
- latest version number does not automatically mean canonical
- historical failures/rejections are reusable project knowledge
- UNRESOLVED does not mean useless
- missing STATE path does not automatically mean lost
- classification must follow validated research history, not filename guessing

At the 2026-10-04 audit:
- local project assets: 9,674 files
- recursive scripts/src Python inventory: 517 files
- canonical STATE research headings: 713
- V2 section-aware classified headings: 636
- STATE asset references: 341
- unique referenced paths: 268
- currently resolving references: 333

The purpose of these indexes is to make future chats USE previous TOTO LABO work rather than repeatedly rediscover it.


### Git project-memory baseline

First project-memory baseline commit:

`d4b71956b68c9b6fc7d35cfbc8796cf40fc6ff2e`

Subject:

`Establish TOTO LABO project memory baseline`

Use this commit as the Git reference point when recovering TOTO LABO context in a new conversation.

The working tree may intentionally contain additional historical/local research assets not included in this baseline.
Do not clean or reset them merely because they are outside this commit.

---

## 15. LATEST CHECKPOINT — 2026-10-05 — MULTISOURCE DICTIONARY v06

This section supersedes the older stopping point / next-action description above where they conflict.

### Current canonical research position

Common multisource dictionary work has already progressed through v06.

Latest artifact:

`data/analysis/toto_labo_multisource_dictionary_v06_fl_team_context_contract.csv`

Dictionary:
- rows = 449
- FootyStats FS60 population/unit semantic contract = FROZEN
- Football LAB CBP108 semantic contract = FROZEN
- Football LAB TEAM_CONTEXT10 semantic meaning/immediate lineage/arithmetic direction = FROZEN
- Football LAB META/IDENTITY/QA37 = not predictive votes
- `attack_col` / `field_strength` = BLOCKED / ORIGIN_UNRESOLVED
- DRAW relations requiring predictive interpretation remain historical-OOF-required
- production weights remain 0
- `P_base` remains UNTOUCHED

### TEAM_CONTEXT10 established lineage

Football LAB raw CBP HTML
→ `table#ls_teamCBP`
→ source columns 6:10
→ normalized BASE4
→ fixture-side HOME/AWAY join
→ TEAM_CONTEXT8
→ derived points/rank fields.

Raw source columns 6–9 are directly labelled:

- 順位
- 勝点
- 得点
- 失点

Season identity on the audited source pages is `2026/27`.

Exact cumulative/current-through-round window semantics are NOT proven and remain:

`2026_27_SOURCE_SNAPSHOT_EXACT_CUMULATIVE_WINDOW_UNRESOLVED`

Do not infer the missing window definition.

TEAM_CONTEXT10 is one correlated contextual lineage:

`FL_TEAM_LEAGUE_RESULT_CONTEXT`

Do not count its ten fields as ten independent votes.

### Current scientific boundary

Semantic understanding is not the same as predictive usefulness.

Do NOT reopen:
- FS60 semantics
- FL CBP108 semantics
- TEAM_CONTEXT10 metric meaning/lineage

unless contradictory source evidence appears.

The next major research question is incremental predictive value under leakage-safe historical/pseudo-OOF validation, including DRAW paths.

DRAW must not be forced.

`P_base` remains the production anchor.

### Round strategy

Do not optimize narrowly for one toto round.

1658 is primarily a development/dictionary/parser/semantic-validation round.

1659 cannot be retrospectively called a blind pre-match test if the necessary pre-kickoff snapshot was not captured.

Future target-round data must be frozen pre-kickoff and evaluated without result-derived tuning.

The broader goal is a reproducible future-round pipeline and stronger long-run prediction process.

### Future acquisition architecture

Target one-command orchestration:

`python scripts/prepare_toto_round.py --round <ROUND>`

Intended flow:

official toto card/votes
→ J.League safe refresh
→ FootyStats URL resolution
→ FootyStats 39-page safe/resumable acquisition
→ FootyStats parse/normalize
→ Football LAB safe/resumable acquisition
→ Football LAB semantic normalization
→ FootyStats × Football LAB semantic comparison/integration
→ totoONE 13-match/predicted-XI layer
→ availability/player-status layer
→ QA
→ production-readiness decision

FootyStats and Football LAB must both be treated as major data sources.

### Simulation direction

Scientific validation order:

10K logic check
→ 100K stability
→ historical OOF / pseudo-OOF
→ 1M precision run only after validation

One million simulations improve Monte Carlo precision; they do not by themselves validate a model.

Future control-room UI must display real model/simulation state and must not alter model logic.

### Git / chat handoff status

Canonical detailed record:

`TOTO_LABO_STATE.md`

Short bootstrap:

`docs/TOTO_LABO_HANDOFF.md`

Project-memory indexes:

- `docs/TOTO_LABO_RESEARCH_INDEX_V2.csv`
- `docs/TOTO_LABO_STATE_ASSET_LINKS.csv`
- `docs/TOTO_LABO_ASSET_INVENTORY.csv`

The repository working tree intentionally contains many historical/local/untracked assets.

Never use:

`git add .`

Never clean/reset the working tree merely to make Git status clean.

Stage only explicitly reviewed project-memory/code/spec artifacts.

At this checkpoint, Git stabilization is the immediate task before further research.

### New-chat recovery instruction

In a new chat:

1. read this HANDOFF first
2. read `RESEARCH_INDEX_V2`
3. read only relevant sections of canonical root `TOTO_LABO_STATE.md`
4. use `STATE_ASSET_LINKS`
5. use `ASSET_INVENTORY`
6. open exact artifacts only as needed

Do not begin with broad repository rediscovery.

The immediate research continuation point after Git stabilization is:

`data/analysis/toto_labo_multisource_dictionary_v06_fl_team_context_contract.csv`

and the next scientific phase is leakage-safe historical/pseudo-OOF evaluation of resolved candidate information, with special attention to DRAW-path information and correlated-feature control.

## PLAYER/XI CANONICAL RESTART — 2026-10-05

Recovered research lineage:
- Round1653: multisource Player/Lineup architecture designed.
- Round1654: FootyStats player strength + J.League identity/crosswalk implemented; Football LAB TEAM CBP research implemented.
- Round1656: Football LAB TEAM matchup matrix completed; FS-based predicted/actual XI strength engine operational.
- Round1656 Football LAB PLAYER asset is LEAGUE_TOP30_RANKING_ONLY and must not be treated as complete player coverage.
- Full quantitative multisource Player Utility is NOT proven complete.
- PLAYER -> lambda / H-D-A production transport remains BLOCKED_BY_HISTORICAL_OOF.
- P_base remains canonical anchor; PLAYER/FL production coefficients remain 0.

Do not redesign PLAYER/XI from scratch.

NEXT:
Transport the existing Round1656 FS-XI operational engine minimally to Round1658 predicted XI.
Before reading Round1658 results:
1. QA 13 matches / 26 teams / 286 predicted starters.
2. preserve identity confidence / position mismatch / minutes / reliability / imputation flags.
3. freeze XI/player-only output.
4. compare FS-only / FL-team-only / XI-player-only source-isolated views.
5. only afterward investigate combined mechanisms.
6. no Round1658 result-fitting and no P_base mutation.

Full checkpoint:
TOTO_LABO_STATE.md
section: 2026-10-05 PLAYER/XI RESEARCH LINEAGE RECOVERY — CANONICAL CHECKPOINT

## ROUND1658 FS-XI FROZEN TRANSPORT COMPLETE — 2026-10-05

The previous `PLAYER/XI CANONICAL RESTART` continuation has now been completed.

Do NOT repeat the Round1658 FS-XI transport or rediscover its identity/crosswalk logic.

### Completed

Round1658 totoONE predicted XI:
- 13 matches
- 26 sides
- 286 predicted starters

FS-XI identity/strength:
- OLD_MASTER_CANONICAL = 193
- FS_CLUB_SHIRT_VALIDATED = 72
- accepted = 265 / 286 = 92.66%
- unresolved = 20
- explicit identity conflict = 1
- missing != zero
- unresolved identity/position was not invented

Frozen player artifact:
`data/analysis/toto1658_xi_fs_player_frozen_transport_v01.csv`

Frozen player SHA256:
`c140e71d76a4bef12953111293fe119d305852078020e2c330828ffcb16e5278`

Canonical scripts:
- `scripts/build_toto_xi_fs_frozen_transport_v01.py`
- `scripts/build_toto_xi_fs_team_match_v01.py`

Git implementation commit:
`1082f87` — `Add frozen FS XI transport and research aggregation`

### Team/match research layer completed

Outputs:
- `data/analysis/toto1658_xi_fs_player_legacy_imputed_v01.csv`
- `data/analysis/toto1658_xi_fs_team_value_coverage_sensitivity_v01.csv`
- `data/analysis/toto1658_xi_fs_match_research_channels_v01.csv`

QA:
- player rows = 286
- team rows = 26
- match rows = 13
- all sides = exactly 11 predicted starters
- resolved starting GK = 24 / 26 sides
- unknown GK = 柏, 磐田
- XI_FINISH_VS_KEEPER blocked matches = 2, 9

VALUE / COVERAGE / SENSITIVITY are separate concepts.

Largest missing-player sensitivity:
- 柏 = 1.695838, coverage 7/11
- 大分 = 1.092978, coverage 7/11
- 横浜FC = 0.638000, coverage 10/11

Unknown position is not invented.
Unknown GK is not replaced by league-average GK merely to complete the feature.
No second reliability weighting is allowed because reliability shrink is already embedded in FS player strength.

### Functional research channels

Transported from the recovered Round1656 lineage:
- XI_ATTACK_VS_DEF_GAP
- XI_BUILD_VS_DEF_GAP
- XI_WIDTH_VS_DEF_GAP
- XI_FINISH_VS_KEEPER_GAP

These channels are correlated and have different scales.

Do NOT:
- count them as independent votes
- simply sum them
- invent a beta
- directly modify lambda
- directly modify H/D/A probabilities

### Production status

P_base remains the canonical production anchor.

`XI_DIRECT_GOAL_HAZARD_TRANSPORT = 0`

`XI_PRODUCTION_BETA = 0.0`

`PRODUCTION_PLAYER_COEFFICIENT = 0.0`

`XI_TRANSPORT_STATUS = RESEARCH_ONLY_UNCALIBRATED`

PLAYER/XI -> lambda / score distribution / H-D-A remains:
`BLOCKED_BY_HISTORICAL_OOF`

Round1658 results were not used in the frozen XI transport.

### CURRENT RESTART POINT

Do NOT repeat:
- PLAYER/XI architecture design
- Round1656 lineage recovery
- Round1658 FS-XI identity reconstruction
- club+shirt bridge validation
- Round1658 player/team aggregation
- GK missingness investigation

Continue from the frozen Round1658 artifacts.

NEXT scientific sequence:
1. preserve source isolation
2. compare FS-team-only / Football LAB-team-only / FS-XI-player-only mechanisms
3. identify agreement, disagreement and correlated evidence
4. inspect DRAW-relevant mechanisms without forcing draws
5. reconstruct leakage-safe historical PLAYER/XI availability
6. perform historical OOF / pseudo-OOF
7. calibrate PLAYER/XI transport only if incremental value is demonstrated
8. keep all production coefficients at 0 until then
9. only after validation proceed 10K -> 100K -> historical OOF -> 1M simulation precision

Full detailed checkpoint:
`TOTO_LABO_STATE.md`
section:
`2026-10-05 ROUND1658 FS-XI FROZEN TRANSPORT — CANONICAL CHECKPOINT`

## ROUND1658 FS-XI FROZEN TRANSPORT COMPLETE — 2026-10-05

The previous `PLAYER/XI CANONICAL RESTART` continuation has now been completed.

Do NOT repeat the Round1658 FS-XI transport or rediscover its identity/crosswalk logic.

### Completed

Round1658 totoONE predicted XI:
- 13 matches
- 26 sides
- 286 predicted starters

FS-XI identity/strength:
- OLD_MASTER_CANONICAL = 193
- FS_CLUB_SHIRT_VALIDATED = 72
- accepted = 265 / 286 = 92.66%
- unresolved = 20
- explicit identity conflict = 1
- missing != zero
- unresolved identity/position was not invented

Frozen player artifact:
`data/analysis/toto1658_xi_fs_player_frozen_transport_v01.csv`

Frozen player SHA256:
`c140e71d76a4bef12953111293fe119d305852078020e2c330828ffcb16e5278`

Canonical scripts:
- `scripts/build_toto_xi_fs_frozen_transport_v01.py`
- `scripts/build_toto_xi_fs_team_match_v01.py`

Git implementation commit:
`1082f87` — `Add frozen FS XI transport and research aggregation`

### Team/match research layer completed

Outputs:
- `data/analysis/toto1658_xi_fs_player_legacy_imputed_v01.csv`
- `data/analysis/toto1658_xi_fs_team_value_coverage_sensitivity_v01.csv`
- `data/analysis/toto1658_xi_fs_match_research_channels_v01.csv`

QA:
- player rows = 286
- team rows = 26
- match rows = 13
- all sides = exactly 11 predicted starters
- resolved starting GK = 24 / 26 sides
- unknown GK = 柏, 磐田
- XI_FINISH_VS_KEEPER blocked matches = 2, 9

VALUE / COVERAGE / SENSITIVITY are separate concepts.

Largest missing-player sensitivity:
- 柏 = 1.695838, coverage 7/11
- 大分 = 1.092978, coverage 7/11
- 横浜FC = 0.638000, coverage 10/11

Unknown position is not invented.
Unknown GK is not replaced by league-average GK merely to complete the feature.
No second reliability weighting is allowed because reliability shrink is already embedded in FS player strength.

### Functional research channels

Transported from the recovered Round1656 lineage:
- XI_ATTACK_VS_DEF_GAP
- XI_BUILD_VS_DEF_GAP
- XI_WIDTH_VS_DEF_GAP
- XI_FINISH_VS_KEEPER_GAP

These channels are correlated and have different scales.

Do NOT:
- count them as independent votes
- simply sum them
- invent a beta
- directly modify lambda
- directly modify H/D/A probabilities

### Production status

P_base remains the canonical production anchor.

`XI_DIRECT_GOAL_HAZARD_TRANSPORT = 0`

`XI_PRODUCTION_BETA = 0.0`

`PRODUCTION_PLAYER_COEFFICIENT = 0.0`

`XI_TRANSPORT_STATUS = RESEARCH_ONLY_UNCALIBRATED`

PLAYER/XI -> lambda / score distribution / H-D-A remains:
`BLOCKED_BY_HISTORICAL_OOF`

Round1658 results were not used in the frozen XI transport.

### CURRENT RESTART POINT

Do NOT repeat:
- PLAYER/XI architecture design
- Round1656 lineage recovery
- Round1658 FS-XI identity reconstruction
- club+shirt bridge validation
- Round1658 player/team aggregation
- GK missingness investigation

Continue from the frozen Round1658 artifacts.

NEXT scientific sequence:
1. preserve source isolation
2. compare FS-team-only / Football LAB-team-only / FS-XI-player-only mechanisms
3. identify agreement, disagreement and correlated evidence
4. inspect DRAW-relevant mechanisms without forcing draws
5. reconstruct leakage-safe historical PLAYER/XI availability
6. perform historical OOF / pseudo-OOF
7. calibrate PLAYER/XI transport only if incremental value is demonstrated
8. keep all production coefficients at 0 until then
9. only after validation proceed 10K -> 100K -> historical OOF -> 1M simulation precision

Full detailed checkpoint:
`TOTO_LABO_STATE.md`
section:
`2026-10-05 ROUND1658 FS-XI FROZEN TRANSPORT — CANONICAL CHECKPOINT`


## MULTISOURCE PLAYER UTILITY RECOVERY — 2026-10-06 MORNING STOP

This supersedes the older instruction to begin by rediscovering PLAYER/XI source assets.

Confirmed existing lineage:
Fansaka base power
-> J.League official player-stat join
-> J.League adjustment
-> `player_power_fp_jl`
-> Round1649 predicted-XI team aggregation.

Key assets:
- `build_fansaka_player_power.py`
- `build_fansaka_player_power_v2.py`
- `data/players/fansaka_j1_2027_r1_with_jleague_v1.csv`
- `data/players/fansaka_j1_2027_r1_jleague_match_audit_v1.csv`
- `data/players/fansaka_j1_player_power_v3_jleague.csv`
- `data/analysis/toto1649_predicted_xi_strength_jleague_fansaka_20260901_v1.csv`

Important:
- existing Fansaka scripts create `player_power_fp`;
- a later existing layer creates `jl_form_score`, `jl_power_adjustment`, `player_power_fp_jl`;
- exact generator/formula/validation lineage of that later layer remains to be recovered;
- Round1649 already aggregated predicted XI into Fansaka strength plus J.League xG/assist/tackle/intercept/pass metrics;
- these assets are currently governance UNRESOLVED;
- do NOT redesign this layer yet;
- do NOT simply average it with FootyStats or Football LAB;
- do NOT modify P_base;
- Round1658 results have not been used.

CURRENT RESTART POINT:
Recover the exact existing generator and validation lineage for the J.League adjustment to Fansaka, then recover FL PLAYER semantics, then construct the FS/Fansaka/JLeague/FL semantic-overlap map.

After that, create source-isolated Round1658 player blocks and move to historical OOF before any production transport.

Full detail:
`TOTO_LABO_STATE.md`
section:
`2026-10-06 MULTISOURCE PLAYER UTILITY RECOVERY — MORNING CHECKPOINT`

## 2026-10-07 FL PLAYER x FS PLAYER SEMANTIC RECOVERY — STOP

Detailed canonical record: TOTO_LABO_STATE.md (2026-10-07 FL PLAYER x FS PLAYER SEMANTIC RECOVERY checkpoint).

COMPLETED: Fansaka/JLeague lineage recovery; FL PLAYER semantics; FL-to-JLeague-to-FS identity recovery; J3 rescue HIGH104/REVIEW10; FL x FS semantic-overlap study; frozen 14-row semantic map with 6 DUPLICATE_OVERLAP rows.

DO NOT REPEAT the FL x FS semantic study from scratch. Canonical artifact: data/analysis/football_lab_footystats_player_semantic_map_1656_v01.csv

RESTART: build the four-source PLAYER semantic map across Fansaka / J.League official / FootyStats / Football LAB. Classify duplicate-correlated, unique candidate, role-context, availability-context, and unresolved information. Then connect only understood components to Round1658 XI as source-isolated research blocks and require historical OOF before fusion or PLAYER-to-lambda transport.

GUARDS: P_base unchanged; production player coefficient 0.0; Round1658 result unused; multisource fusion not validated; PLAYER-to-lambda blocked by historical OOF.


## 2026-10-07 AM — PLAYER semantic recovery checkpoint

- JLeague official <-> FootyStats PLAYER strict identity is FROZEN at 566 players using existing 1656 exact crosswalk. JL join 566/566; FS join 566/566; do not restart identity exploration.
- JL vs FS six-axis, controlling JL minutes within role: strong/meaningful overlap examples include FW shoot->finishing 0.531, FW xG->finishing 0.479, MF chance_create->attack 0.430, MF pass->build_up 0.641, MF pass_rate->build_up 0.564, MF opponent-area-pass->build_up 0.513, MF dribble->width_carry 0.573, MF cross->width_carry 0.643, GK save_rate->keeper 0.871. These are correlated lineages, not independent votes.
- Defensive JL candidates were not strongly absorbed by FS six axes: DF tackle->defensive 0.084, block 0.203, recovery -0.200, aerial 0.286, duels 0.032. Cross-axis check also remained generally weak except recovery vs attack 0.300 / width-carry 0.344. Low correlation is NOT predictive validation.
- Existing FS raw PLAYER universe recovered: data/players/footystats_2026_toto1656_player_universe_v01.csv = 668x275; raw defensive five metrics coverage 579/668; identity key Current Club+full_name+position+minutes has zero duplicates.
- JL vs FS raw semantic comparison (role + JL-minutes controlled partial Spearman): shot 0.737, xG 0.540, cross 0.721, chance_create 0.056, pass 0.756, long_pass 0.097, through_pass -0.064, dribble 0.669, tackle 0.196, block 0.222, interception 0.153 (n=27), aerial 0.656, duels 0.197, GK saves 0.776. Strong pairs are DUPLICATE_OVERLAP candidates; weak same-name pairs are DEFINITION_MISMATCH_OR_UNIQUE_CANDIDATE, not proven unique/predictive. FS raw can retain phenomena lost by six-axis compression.
- Fansaka identity warning: fansaka_j1_player_power_v3_jleague.csv jleague_player_id and current 1656 exact crosswalk jleague_player_id have ZERO overlap despite both int64; namespaces/lineage differ. Never directly join them on this field.
- Existing Fansaka<->FS audits recovered but currently non-reproducible: audit_fansaka_footystats_strength_overlap_v01.py gives DIRECT_UNIQUE_MATCH=0; v02 gives CROSSWALK=0/JOINED=0 because its 1645 dependency has fantasy_player_name 281/286 but footystats_player_name 0/286. Both scripts misleadingly print PASS even with zero matches. Treat as LEGACY_AUDIT_CURRENTLY_UNREPRODUCIBLE; do not rebuild from scratch unless needed. Existing historical Fansaka OOF evidence remains valid separately and production coefficient stays 0.
- Existing FL<->FS player semantic map remains frozen at data/analysis/football_lab_footystats_player_semantic_map_1656_v01.csv. Do not redo it.
- NEXT: freeze a four-source PLAYER semantic map (Fansaka / JLeague official / FootyStats raw+axes / Football LAB PLAYER), preserving source population differences and classifications such as DUPLICATE_OVERLAP, DEFINITION_MISMATCH, ROLE_CONTEXT, UNIQUE_CANDIDATE_NEEDS_OOF, AVAILABILITY_CONTEXT, UNAVAILABLE. Then connect only validated/non-duplicated candidates to 1658 XI as research-only coefficient=0 and proceed to historical OOF before any production transport.
- Governance unchanged: P_base is production anchor; no P_base mutation; no simple source averaging; correlated metrics are not independent votes; missing != zero; predicted XI != confirmed XI; PLAYER production coefficient=0 until historical OOF; do not force draws.
