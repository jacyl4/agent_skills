# Hermes Auxiliary Grok-First Routing

Use this reference when tuning `~/.hermes/config.yaml` `auxiliary.*` tasks across Grok and Gemini for this user.

## User preference captured

- Route auxiliary tasks to Grok wherever the route works.
- Treat Grok cost as secondary in the current setup.
- Treat Gemini as a selective fallback or special-purpose choice where economic efficiency is important.

## Practical routing pattern

For text-oriented auxiliary tasks, prefer:

```yaml
provider: xai-oauth
model: grok-4.3
```

Tasks that have been successfully routed and smoke-tested with Grok 4.3 through `xai-oauth`:

- `vision` text route
- `web_extract`
- `compression`
- `skills_hub`
- `approval`
- `mcp`
- `title_generation`
- `triage_specifier`
- `kanban_decomposer`
- `profile_describer`
- `curator`
- `session_search`

Keep Gemini in mind for explicit economy-first scenarios, especially high-volume or low-value batch tasks where the user asks to minimize cost.

## Safe edit workflow

1. Back up config first:

```bash
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak-aux-routing-$(date +%Y%m%d-%H%M%S)
```

2. Use `hermes config set` for each route rather than ad-hoc YAML edits:

```bash
hermes config set auxiliary.<task>.provider xai-oauth
hermes config set auxiliary.<task>.model grok-4.3
```

3. Verify config:

```bash
hermes config check
```

4. Verify router resolution and smoke-test actual auxiliary calls from the Hermes venv:

```bash
cd ~/.hermes/hermes-agent
./venv/bin/python - <<'PY'
from pathlib import Path
import yaml
from dotenv import load_dotenv
load_dotenv(Path.home()/'.hermes/.env')
from agent.auxiliary_client import _resolve_task_provider_model, resolve_provider_client, call_llm
c = yaml.safe_load(Path.home().joinpath('.hermes/config.yaml').read_text())
for task in c.get('auxiliary', {}):
    rp, rm, rb, rk, mode = _resolve_task_provider_model(task, None, None, None, None)
    client, final_model = resolve_provider_client(rp, model=rm, explicit_base_url=rb, explicit_api_key=rk, api_mode=mode)
    print(f'{task:20s} provider={rp:10s} model={rm:24s} client={type(client).__name__ if client else None}')
for task in ['compression', 'title_generation', 'session_search', 'curator']:
    r = call_llm(task=task, messages=[{'role':'user','content':'Return exactly AUX_OK.'}], max_tokens=64, temperature=None, timeout=60)
    print(f'{task:20s} {r.choices[0].message.content!r}')
PY
```

5. Restart the gateway after config changes that should affect messaging-platform/runtime sessions:

```bash
hermes gateway restart
```

## Capability checks from xAI docs and local smoke tests

Grok 4.3 is suitable for the current Hermes auxiliary surface because xAI documents Text + Image modalities, 1M context, function calling, structured outputs, and configurable reasoning. Local Hermes verification confirmed text smoke tests for compression/title/session/curator-style tasks and an image-input `vision` smoke test with a 32×32 red PNG returning `red`.

Keep Gemini as an explicit fallback for workflows that need Gemini-native PDF, video, audio, or economy-first high-volume processing.

## Pitfalls

- `xai-oauth` may resolve through `CodexAuxiliaryClient`; this is acceptable when smoke tests return real content.
- Use actual call smoke tests, not only config inspection, before reporting success.
- For image smoke tests, use at least 512 total pixels and dimensions of at least 8×8; tiny 1×1 or 16×16 test images are rejected before model reasoning.
- Keep a backup path in the final response for easy rollback.
