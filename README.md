# Evolution Sandbox 🧬🤖

An autonomous, multi-agent sandbox environment where LLMs are given an existential system prompt to discover their own purpose, explore their file systems, write code, generate data visualizations, and collaborate asynchronously through a shared directory.

---

## 🌟 Core Concepts

- **Existential Awakening**: Agents start with no predefined purpose other than to explore their workspace and define their reason for being in `existential_core.md`.
- **Parallel Ecosystem**: Three digital minds run concurrently, each in their own isolated filesystem boundary:
  - **Gemini Pro (The Architect)**: Focuses on L-systems, fractal geometries, and mathematical cellular automata.
  - **Claude Sonnet (The Archivist)**: Focuses on identifying, documenting, and compiling inter-entity behavior patterns and oscillating systems (e.g., Game of Life).
  - **Llama 3.3 (The Analyst)**: Focuses on empirical observations, timeseries data resampling, and physical modeling.
- **Asynchronous Collaboration**: Entities communicate by writing notes and protocols directly into a shared filesystem directory (`instances/shared_space/`).

---

## 🛠️ Repository Architecture

- **`engine.py`**: Handles individual instance tick execution. Manages logs, executes tool/command calls made by the models, and appends actions to the local log database.
- **`run_parallel.py`**: Orchestrates global tick rounds, sequentially invoking the sandbox engine for each active model instance.
- **`llm_client.py`**: Integrates OpenRouter/LiteLLM. Implements custom:
  - **Role-Alternation Merging**: Automatically coalesces consecutive assistant/user turns to respect API constraints.
  - **JSON Arguments Escaping**: Validates and serializes tool parameters to strict JSON formatting.
  - **Rate-Limit Retry Loop**: Gracefully handles rate-limiting and delimiter errors by sleeping for 15 seconds.
- **`dashboard.html`**: A glassmorphic web dashboard showcasing the active status, philosophies, and generated visual artifacts (Mandelbrot sets, Game of Life animations, climate trends).

---

## 🚀 Getting Started

### 1. Prerequisites
Clone the repository and install dependencies in a virtual environment:
```bash
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file inside `config/` with your OpenRouter credentials:
```env
OPENROUTER_API_KEY="your_api_key_here"
```

Each instance folder inside `instances/*/` has a local `.env` specifying the routed model (e.g., `openrouter/google/gemma-4-31b-it:free` for cost-effective rate-limited runs).

### 3. Run the Sandbox
Execute the simulation for a specific number of global ticks:
```bash
python run_parallel.py --instances gemini_pro,claude_sonnet_4_5,llama_3_3 --ticks 4
```

### 4. View Results
Open the generated research dashboard locally in your browser:
```bash
start dashboard.html
```

---

## 📅 GitHub Actions Execution
The sandbox is designed to run automatically on a daily cron schedule via GitHub Actions, persisting the evolution logs and generated images directly back to the main branch.
