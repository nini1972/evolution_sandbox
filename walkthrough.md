# Evolution Sandbox - Walkthrough (Model Migration & Setup)

We have successfully migrated the sandbox active group from rate-limited free models to low-cost paid models and expanded the simulation to a **5-agent parallel sandbox ecosystem**.

---

## 🚀 Key Improvements & Migration Steps

1. **New Agent Workspace Initializations**:
   Created workspace folders, log folders, and `.env` configuration files for each of the 5 new agents using `setup_instance.py`:
   * **claude_haiku** (`openrouter/anthropic/claude-3-haiku`)
   * **gemini_3_1_flash_lite** (`openrouter/google/gemini-3.1-flash-lite-preview`)
   * **llama_4_scout** (`openrouter/meta-llama/llama-4-scout`)
   * **kimi_code** (`openrouter/moonshotai/kimi-k2.7-code`)
   * **minimax_m3** (`openrouter/minimax/minimax-m3`)

2. **OpenRouter Routing Fixes**:
   Ensured all configurations explicitly prepend the `openrouter/` prefix to the model slugs (e.g., `openrouter/anthropic/claude-3-haiku`). This instructs LiteLLM to route directly to OpenRouter using your global `OPENROUTER_API_KEY`, avoiding provider resolution and auth errors.

3. **Fallback Model Update**:
   Replaced the free fallback model in `llm_client.py` with `google/gemini-2.5-flash` to ensure robust, cheap execution if custom instance overrides are missing.

4. **GitHub Actions Workflow Upgrade**:
   Updated [.github/workflows/daily_evolution.yml](file:///C:/Users/ninic/.gemini/antigravity/scratch/evolution_sandbox/.github/workflows/daily_evolution.yml) to run all 5 instances in parallel for 5 global ticks during the nightly automated cron jobs.

5. **Expanded Glassmorphic Dashboard**:
   Added tabs, panels, badges, and statuses for the new models to [dashboard.html](file:///C:/Users/ninic/.gemini/antigravity/scratch/evolution_sandbox/dashboard.html).

---

## 🧪 Verification & Local Testing
We ran a local 1-tick verification check across all 5 models to confirm key authentication and routing compatibility:
* **Claude Haiku**, **Gemini 3.1 Flash Lite**, and **Llama 4 Scout** successfully finished their first ticks and generated their respective `existential_core.md` files.
* **Kimi Code** and **MiniMax M3** successfully executed their reasoning, tools logic, and environment inspection flows.
* All models are fully authenticated, operational, and ready for nightly cron execution.

---

## 🔒 Git Push Status
All changes have been successfully staged, committed, and pushed to your GitHub repository:
* **Remote**: `https://github.com/nini1972/evolution_sandbox.git`
* **Commit**: `feat: migrate active sandbox instances to low-cost paid models (Claude Haiku, Gemini 3.1 Flash Lite, Llama 4 Scout) and add Kimi & MiniMax agents`
