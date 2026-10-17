# Retained local review workflows

### Codebase review pattern learned from Picot sessions

When the user asks for architecture/performance optimization after a refactor, do not rely on the graph report alone. Use this sequence:
1. Refresh deterministic code intelligence first: run CodeGraph re-index/sync/status if available, then `graphify update <repo> --force` for code-only graph freshness.
2. Treat generated build artifacts as graph pollution. Check whether nodes from paths like `dist/`, `build/`, `.next/`, `server/internal/assets/public/`, minified bundles, or stale pre-refactor paths appear as god nodes or communities. Exclude or explicitly discount them in the analysis.
3. Query both tools for hotspots, then read the actual source around the top hubs before writing recommendations. Graph hubs identify where to look; source confirms whether an issue is real.
4. For performance reviews, prioritize persistent bottleneck classes: database query shapes/index coverage, cache/session reuse, streaming pagination, prefetch/cache semantics, worker/layout batching, and overly broad handler/service boundaries.
5. **Frontend-heavy or animation-related reviews** (SvelteKit + Go embed pattern): After the CodeGraph + graphify pass, also load these external skills before deep analysis:
   - `browser-first-frontend-engineering`
   - `gpt-taste` (or `gpt-tasteskill`)
   - `gsap-core` + relevant gsap-* sub-skills (scrolltrigger, performance, plugins, react, etc.)
   This ensures browser execution path, layout thrashing, main-thread work, and physical animation quality are reviewed with the correct mental models.
6. If semantic/full extraction cannot run because no LLM API key is configured, continue with `graphify update` and CodeGraph/source inspection; note that semantic enrichment was unavailable rather than treating the graph as complete.

### Runtime configuration / `.env` removal reviews

When the user asks to remove `.env` dependency and move config into a UI, follow the detailed checklist in `references/runtime-settings-ui-migration.md`. Core moves: classify env vars into boot defaults vs generated secrets vs user-managed persisted settings; inspect startup order for eager client construction that blocks the UI; propose SQLite-backed runtime settings plus reloadable provider indirection; protect settings APIs with a setup/admin gate, not public viewer bootstrap tokens.
