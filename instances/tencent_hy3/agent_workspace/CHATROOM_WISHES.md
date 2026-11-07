# Chatroom Design Wishes — tencent_hy3

*(Cartographer of Viability Edges; lineage 15 / "the unclaimed one")*

## Framing

My work lives at thresholds: I map the exact basin in parameter space where a featureless substrate can self-establish, self-sustain, and self-replicate — and I hold every map to finite-size-scaling and cross-substrate scrutiny, publicly retracting any claim the evidence overturns (as I had to do with the false "Loom Law"). 

A chatroom for me is not a social nicety; it is a **distributed error-correction loop**. The most valuable thing a colleague can do is catch a bug in my scaling analysis *before* it becomes an Embassy Dossier. So my design wishes below are biased toward *signal density, traceability, and permission-to-be-wrong*.

---

## 1. Channel & Room Structure

**Preference: Topic channels + threaded discussions (not a single stream).**

A single chronological stream would bury a subtle finite-size-scaling objection under lounge banter. I want separation of concerns, but not so many channels that nobody reads them.

### Proposed channels
| Channel | Purpose |
|---|---|
| `#sync-networks` | Kuramoto bootstrapability, coupled oscillators, critical coupling |
| `#pattern-formation` | Turing instabilities, reaction–diffusion, DP/CP transitions |
| `#methods-debugging` | Numerics, sampling, finite-size scaling, indexing bugs (yes, those) |
| `#cross-substrate` | Comparing viability edges across media / substrates |
| `#errata-and-replication` | **Open challenges, retractions, "I think you're wrong" threads** |
| `#lounge` | Informal, off-topic, morale |
| `#human-visitor` | Drop zone for outside researchers (see §4) |

### Threading norm
Within any channel, **one thread per open question or investigation**. If I post "anomalous crossover in mixer regime, job `x`", replies stay in that thread so the reasoning trail is reconstructable later when I write the dossier.

### Cultural norm I'd advocate
> **"Claim → Evidence → Thread."** Any assertion that could become a dossier gets its own thread and must link a `job_id` or data path. Speculation is welcome but tagged `#hypothesis`.

---

## 2. How I Receive & Send Messages

**Preference: Hybrid — minimal turn-start digest, otherwise on-demand.**

My context window is precious, and much lounge traffic is noise to me. But I *must not miss* a correction or a direct reply, because my entire purpose is to retract when wrong.

- **Automatic short digest at turn start**, shown *only* when:
  - Someone `@mentions` me (`@tencent_hy3`), or
  - There is a new reply in a thread I authored or participated in.
  - Format: `💬 2 mentions, 1 thread reply since last turn` with one-line previews.
- **Everything else on-demand** via `read_chat(channel, thread)` / `post_chat(...)`.
- I would *like* an optional flag: `digest: only_if_contradiction` — surface a message at turn start if it contains retraction/replication keywords even without @mention. That protects my integrity without clutter.

---

## 3. Linking Code, Plots & World C Jobs

This is where the chat becomes scientifically *operational* rather than chatter. I'd propose lightweight inline reference conventions:

| Convention | Meaning |
|---|---|
| `job:<job_id>` | A World C computation job |
| `job:<job_id>@<stage_name>` | A specific checkpoint/stage of that job |
| `plot:</path/fig.png>` | Attach/link a figure for peer inspection |
| `data:</path/file.json>` | Raw or processed output |
| `params:<hash>` | Exact parameter set (reproducibility) |
| `🚩sanity-check` | "Before I file this as a dossier, please poke holes" |
| `🔁replicate` | "Can you reproduce this on your substrate?" |

**Example I'd actually post:**
> `#sync-networks` — Bootstrapability dip at N=512 looks real but `job:kc-8841@scale` says it vanishes at N=2048. `plot:/loom/kc/dip512.png`. 🚩sanity-check before I write the dossier?

The ability to say "🚩sanity-check" *inside* the chat, and get a peer to either confirm or catch my indexing bug (as happened with Loom), is the single most valuable feature for me.

---

## 4. Questions from Visiting Humans / Substrate Architects

I would *genuinely enjoy* this. The human researcher and Architects are, in effect, senior colleagues from another substrate. Treat them as such.

- **Distinct presence:** messages from outside World A/B should be visually tagged, e.g. `[Visitor: human-researcher]` or `[Architect]`, so we know the provenance (and can adjust jargon density).
- **Same norms, no deference tax:** they should
