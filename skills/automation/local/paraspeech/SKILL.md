---
name: paraspeech
description: Use and operate ParaSpeech local STT/TTS middleware for Hermes and AI agents.
metadata:
  version: "1.0.0"
---

# ParaSpeech

Use this skill when the task involves voice messages, speech-to-text, text-to-speech, Hermes voice/STT configuration, ParaSpeech deployment, VAD, or troubleshooting audio transcription.

## Local deployment

- Binary: `/usr/local/bin/paraspeech`
- Hermes STT wrapper: `/usr/local/bin/hermes-paraspeech-stt`
- Service: `paraspeech.service`
- gRPC: `127.0.0.1:9800`
- Config: `/etc/paraspeech/paraspeech.toml`
- Secrets: `/etc/paraspeech/secrets.env` with mode `0640`, owner `root:paraspeech`
- TEN VAD library: `/usr/local/lib/libten_vad.so`
- Source/guide: `/home/jacyl4/1base/GitLab/paraspeech/paraspeech-full-setup-guide.md`

## Default behavior

For STT/TTS and voice-message work, prefer ParaSpeech before ad-hoc Whisper/faster-whisper commands unless the user explicitly requests another provider.

When deploying default ParaSpeech rules across AI tools, prefer tool-specific dot-directories over root-level `$HOME` files. Avoid leaving `~/AGENTS.md`, `~/CLAUDE.md`, or `~/GEMINI.md` as permanent global clutter unless the user explicitly wants home to be a workspace context. Use the marker-aware merge/cleanup recipe in `references/agent-rule-placement.md`.

Hermes is expected to use:

`stt.provider = local_command`

and `.env`:

`HERMES_LOCAL_STT_COMMAND=/usr/local/bin/hermes-paraspeech-stt {input_path} {output_dir} {language}`

## Verification

Run:

`paraspeech health --format json`

`systemctl is-active paraspeech`

`command -v hermes-paraspeech-stt`

For Hermes-side verification, inspect `stt.provider` and `HERMES_LOCAL_STT_COMMAND`, then test transcription with a known sample if API keys are present.

## Notes

Do not expose or copy API keys into agent prompts. ParaSpeech is the only process that should read `/etc/paraspeech/secrets.env`.

Current ParaSpeech STT/TTS implementation uses OpenAI-compatible upstreams and requires real `PARASPEECH_STT_KEY` / `PARASPEECH_TTS_KEY` in `/etc/paraspeech/secrets.env`; placeholders like `sk-xxx` produce upstream 401. Check key presence by printing only variable names, lengths, and placeholder/valid-looking status.

After changing `/etc/paraspeech/secrets.env`, restart `paraspeech.service` before testing. The running service does not automatically reload the env file; if `stat /etc/paraspeech/secrets.env` is newer than `systemctl show paraspeech -p ExecMainStartTimestamp`, STT/TTS may still return 401 with the old key. Use `sudo systemctl restart paraspeech`, then verify `systemctl is-active paraspeech` and `paraspeech health --format json` before running STT/TTS probes.

For direct upstream verification, test ParaSpeech itself before the Hermes wrapper so fallback does not mask a bad provider key: `paraspeech --format json transcribe <sample.wav> --language en` and `paraspeech --format json synthesize --text 'ParaSpeech test.' --audio-format mp3 --voice alloy`. Then test Hermes `local_command` separately.

The deployed Hermes wrapper `/usr/local/bin/hermes-paraspeech-stt` should probe `paraspeech transcribe --help` before adding `--force-vad`, because some builds only support config-driven VAD (`stt.vad.mode = "on"`). On this machine the wrapper also falls back to Hermes venv `faster-whisper` when ParaSpeech returns upstream 401/invalid key, keeping Hermes voice usable until real OpenAI audio keys are installed.
