# Runtime settings / `.env` removal analysis pattern

Use this when a codebase analysis task asks to remove runtime `.env` dependency and move configuration into an application UI or persisted settings store.

## Analysis sequence

1. Refresh deterministic code intelligence first: run CodeGraph sync/status and Graphify update, then treat the graph as a navigation map rather than the whole answer.
2. Search for all environment variable readers and deployment env injection points:
   - Go: `os.Getenv`, config `Load()`, `Validate()`
   - Node/TS: `process.env`, `import.meta.env`
   - Docker/systemd/Makefile: `env_file`, `EnvironmentFile`, `-include .env`
3. Classify each `.env` key before proposing design:
   - **Boot defaults**: safe to hardcode/default (`SERVER_HOST=0.0.0.0`, `SERVER_PORT=8080`, SQLite path, cache/upload tuning).
   - **Generated secrets**: must exist but can be generated and persisted on first boot (JWT signing secret, setup token hash).
   - **User-managed secrets/settings**: should be edited through UI and persisted server-side (Cloudflare R2 account/access/secret/bucket/public URL).
   - **Advanced overrides**: can remain optional env vars for operators but must not be required for first boot.
4. Inspect startup order. The key blocker is often not parsing `.env`, but eager construction of clients before the UI can start. If storage/R2 client is created in `main()` before routes/static frontend, propose a degraded/bootstrap mode.
5. Recommend a runtime settings service and provider indirection:
   - persisted settings repository backed by SQLite;
   - secret values not returned by API;
   - `CurrentStore()`/reloadable provider instead of handlers permanently holding a startup-time client;
   - clear `StorageNotConfigured` responses for sync/upload/media paths.
6. Design setup/admin protection explicitly. Do not let existing public viewer/bootstrap tokens protect settings APIs. Prefer a one-time setup token printed to logs or an admin password flow.
7. Map UI placement to existing frontend control surfaces. For Picot-like gallery apps, a dock/control-panel settings button plus modal is less invasive than a new route.
8. Split implementation into phases: no-env boot, settings API, frontend modal, docs/compose cleanup.

## Pitfalls

- Do not suggest storing R2 keys in browser localStorage; server-side sync/upload needs backend credentials and browser storage exposes secrets.
- Do not suggest writing `.env` from the UI as the primary design; it usually requires restarts and conflicts with Docker/containerized operation.
- Do not treat generated frontend assets (`dist/`, `.svelte-kit/`, embedded `server/internal/assets/public/`) as source-level graph evidence; exclude or explicitly discount them.
- If a JWT/public auth bootstrap endpoint exists, check whether it grants only viewer privileges. Settings APIs need a separate admin/setup gate.
