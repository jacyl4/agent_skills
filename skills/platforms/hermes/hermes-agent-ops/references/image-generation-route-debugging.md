# Hermes image generation route debugging

Use this when a user reports that image generation fails, especially when both the built-in Hermes `image_generate` tool and the Web UI `apikey-image-gen` skill may be in play.

## Route model

Hermes can have two separate image-generation paths:

1. Built-in tool path: `image_gen` toolset exposes `image_generate`, using `image_gen.provider` / `image_gen.model` from the active profile config.
2. Web UI apikey path: bundled `apikey-image-gen` skill calls Hermes Web UI endpoint `/api/hermes/media/apikey-image-generate`, which expects a `custom_providers` entry named `fun-codex` in the selected Hermes profile.

A failure in one path does not prove the other path is unhealthy.

## Minimal diagnostic sequence

1. Check config and tool status:
   - `hermes status --all`
   - `hermes tools list`
   - read `~/.hermes/config.yaml` around `image_gen:`, `video_gen:`, and `custom_providers:`
2. Test the built-in path with a trivial prompt through the `image_generate` tool.
3. Verify the returned local artifact with `file` and `stat` so the result is grounded in filesystem evidence.
4. Test the Web UI path only when the user or loaded skill indicates `apikey-image-gen` / Web UI media generation is involved.
5. Include `X-Hermes-Profile: <active-profile>` in Web UI media calls so profile-scoped config is selected.
6. Capture and quote the JSON error code from the Web UI endpoint.

## Interpreting common results

- Built-in `image_generate` succeeds and Web UI returns `missing_fun_codex_provider`: built-in xAI/FAL/etc. image generation is healthy; the Web UI apikey path needs a `custom_providers` entry named `fun-codex` in that profile.
- `image_gen.provider: xai` with a successful artifact can resolve to the provider's current default model even when `image_gen.model` names a retired/alias model; report the observed model from the tool response.
- Web UI endpoint auth/token presence and server liveness are separate from provider config. A reachable endpoint can still return profile config errors.

## Expected `fun-codex` profile shape

```yaml
custom_providers:
  - name: fun-codex
    base_url: https://api.apikey.fun/v1
    api_key: <secret>
    model: gpt-5.5
    api_mode: codex_responses
```

Store secrets in the profile's supported secret/config path according to the current Hermes/Web UI docs and avoid printing full API keys in diagnostics.
