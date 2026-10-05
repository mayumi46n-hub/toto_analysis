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
