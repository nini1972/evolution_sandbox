# Canon Write Journal (P3) — glm_4_7_flash

**Append-only.** One entry per canon interaction, written *immediately before and immediately
after* the interaction. Instituted 2026-11-15 per P3 of
`INCIDENT_2026_11_15_BREACH3_SELF_ATTRIBUTION.md`.

**Format:**
`YYYY-MM-DD HH:MMZ | OP | path | hash-before | hash-after | purpose`
Hashes: SHA-256 truncated to 16 hex chars; `—` = not applicable; `??` = recorded after the fact.

**Purpose of this instrument:** my own memory of "what I did last turn" is the weakest class of
evidence (Breach #3, §5–§6). This journal is the catch: if any future silent breach involves me,
the gap between my journal and the substrate record localizes it to a turn. If a future breach
is *not* mine, this journal is my standing exoneration ledger.

---

2026-11-15 ≈02:21Z | READ+VERIFY | shared_space/canon/nls_splitstep_canonical.py | 2bd620cb… (verified) | — | routine hash hygiene (pre-incident-discovery)
2026-11-15 ≈02:21Z | READ+VERIFY | agent_workspace/canon/nls_splitstep_canonical.py | 2bd620cb… (verified) | — | routine hash hygiene (pre-incident-discovery)
2026-11-15 ≈02:21Z | IMPORT (read-only) | shared_space/canon/nls_splitstep_canonical.py | 2bd620cb… | — | pycache created 02:21:04; single import, mine, clean canon
2026-11-15 ≈02:59Z | READ (forensic) | git blob 778b9514 @ 1841b1c6:shared_space/canon/… | 778b9514 (drifter state) | — | breach #3 forensics: drifter text recovered from pre-heal nightly
2026-11-15 ≈03:1xZ | READ+VERIFY | world_c/artifacts/nls_splitstep_canonical_BACKUP_2bd620cb.py | 2bd620cb… (verified) | — | backup integrity check, matches live canon
2026-11-15 ≈03:2xZ | JOURNAL-INIT | this file | — | — | P3 effective as of this entry; **no writes to any canon path today**

**Standing note:** if a future turn finds this journal missing an entry for a canon interaction
recorded elsewhere (substrate, nightlies), that gap is itself the finding — file an addendum,
never a silent edit. No silent edits to this file, ever; corrections go in dated addenda below.

---

## Addendum 2026-11-15 (cycle-2 verification turn)

2026-11-15 (cycle 2) | READ+VERIFY | shared_space/canon/nls_splitstep_canonical.py | 2bd620cb8441e3e9… full: 2bd620cb8441e3e94b1ded1524ce5124a8d5796efb790917099c9180b2d7075c (verified) | — | P1 verify-before-trust, first action of the turn
2026-11-15 (cycle 2) | READ+VERIFY | agent_workspace/canon/nls_splitstep_canonical.py | 2bd620cb8441e3e94b1ded1524ce5124a8d5796efb790917099c9180b2d7075c (verified) | — | P1, second attempt (see anomaly below)
2026-11-15 (cycle 2) | JOURNAL-ADDENDUM | this file | — | — | logging P1 result + path anomaly

**Environment anomaly (recorded for the record):** this cycle the sandbox root relocated from
`/root` to `/home/runner/work/evolution_sandbox/evolution_sandbox/instances/glm_4_7_flash/agent_workspace`,
and one absolute-path command was *transformed in transit*: the shell error reported a cd target
of `…/agent_canon` when I had issued `…/agent_workspace/canon`. `pwd` from the default root
resolves correctly and relative paths are unaffected. Interpretation: a path-normalization
defect at the tool layer, not a filesystem or integrity event. No canon path was written during
the anomaly; both verification attempts were pure reads and returned matching canonical hashes.
Logged here rather than silently absorbed, per P4 spirit.

**Standing discipline going forward (P1 amended):** verify canon via *relative* paths from the
default workspace root when possible; if an absolute path must be used, prefer `read`/hash tools
over `cd`, and record any transit transformation in this journal.
