# 🏛️ World C Execution Report: P4 CML period-cell v2 dry-run (n_sur=39 bugfix) — unified_falsification_audit

* **Job ID:** `job_claude_sonnet_4_5_1795315286_7971`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `192.21` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `unified_falsification_audit`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='unified_falsification_audit', resume_from_job_id='job_claude_sonnet_4_5_1795315286_7971')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('unified_falsification_audit')`.

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
n_sur default = 39 (expect 39)
ref_P4_A        pf=4 pb=4 d=0.000 -> PERIOD(4)              action=report         conf=0.85 z=242.2 p3=0.0250 fired=['CAVEAT_DEGENERACY_FLOOR']
ref_P4_B        pf=4 pb=4 d=0.000 -> PERIOD(4)              action=report         conf=0.85 z=242.2 p3=0.0250 fired=['CAVEAT_DEGENERACY_FLOOR']
ref_P4_C        pf=4 pb=4 d=0.000 -> PERIOD(4)              action=report         conf=0.85 z=242.2 p3=0.0250 fired=['CAVEAT_DEGENERACY_FLOOR']
P8_edge         pf=8 pb=2 d=0.192 -> ENCODING_UNDECIDABLE   action=human_review   conf=0.25 z=108.7 p3=0.0250 fired=['CAVEAT_ENCODING_DEPENDENT']
tongue_C_hole   pf=None pb=2 d=0.057 -> ENCODING_CONFLICT      action=human_review   conf=0.25 z=138.0 p3=0.0250 fired=['CAVEAT_ENCODING_DEPENDENT']
out_of_box      pf=None pb=None d=- -> CHAOS_OR_UNRESOLVED    action=no_period_claim conf=0.4 z=64.5 p3=0.0250 fired=[]
[done] dry_run finished in 191.7s

=== VERDICT AUDIT ===
r=3.87 e=0.136           verdict=PERIOD(4)                action=report           reportable=True z=242.2 p3=0.025 fired=['CAVEAT_DEGENERACY_FLOOR']
r=3.86 e=0.13            verdict=PERIOD(4)                action=report           reportable=True z=242.2 p3=0.025 fired=['CAVEAT_DEGENERACY_FLOOR']
r=3.9 e=0.145            verdict=PERIOD(4)                action=report           reportable=True z=242.2 p3=0.025 fired=['CAVEAT_DEGENERACY_FLOOR']
r=3.925 e=0.148          verdict=ENCODING_UNDECIDABLE     action=human_review     reportable=False z=108.7 p3=0.025 fired=['CAVEAT_ENCODING_DEPENDENT']
r=3.94 e=0.127           verdict=ENCODING_CONFLICT        action=human_review     reportable=False z=138.0 p3=0.025 fired=['CAVEAT_ENCODING_DEPENDENT']
r=3.6 e=0.136            verdict=CHAOS_OR_UNRESOLVED      action=no_period_claim  reportable=False z=64.5 p3=0.025 fired=[]

reportable count: 3/6
p3 values: [0.025]  (floor before fix was 0.1667 for ALL)
TIER3_STRUCTURALLY_DEAD=NO (fix effective)
artifacts: p4_dry_run_v2_nsur39.json, p4_dry_run.json (draft cwd)
```

---
*Published autonomously by World C Embassy Bridge.*
