# Hermes Media Tools: Grok Routing Notes

Use this when configuring or explaining Hermes image analysis, image generation, and video generation with Grok/xAI models.

## Route separation

- **Image analysis / image understanding**: `vision_analyze`; configured under `auxiliary.vision`. Use a vision-capable chat model such as `grok-4.3` through `xai-oauth` or `xai`.
- **Image generation**: `image_gen` toolset and `image_generate`; configured under `image_gen`. Grok Imagine image models such as `grok-imagine-image` belong here. Image-quality/enhancer models such as `grok-image-quality` belong to the image-generation backend path when supported by the plugin.
- **Video generation**: `video_gen` toolset and `video_generate`; configured under `video_gen`. Grok Imagine video models such as `grok-imagine-video` belong here.
- **Video analysis**: `video` toolset and `video_analyze`; separate from `video_gen`.

## Preferred setup flow

1. Confirm toolsets:
   ```bash
   hermes tools list | grep -E 'image|video|gen'
   ```
2. Configure credentials for xAI:
   ```bash
   hermes auth add xai-oauth
   # or put XAI_API_KEY in ~/.hermes/.env
   ```
3. Use the interactive tool setup for media backends:
   ```bash
   hermes tools
   ```
   Select Image Generation and Video Generation, then choose the xAI/Grok Imagine backend where available.
4. Verify persisted config:
   ```bash
   hermes config
   hermes doctor
   ```
5. Start a new session or run `/reset`; Hermes tool schemas and backend capability descriptions are built at session start.

## Common explanation pattern

When the user asks whether Hermes image analysis can use Grok, answer yes and clarify that image analysis uses the `vision` route, while Grok Imagine models are generation models. Example target config shape:

```yaml
auxiliary:
  vision:
    provider: xai-oauth
    model: grok-4.3

image_gen:
  provider: xai-oauth
  model: grok-imagine-image
  # quality_model: grok-image-quality   # if supported by the active image_gen plugin

video_gen:
  provider: xai-oauth
  model: grok-imagine-video
```

Prefer `hermes tools` over hand-editing exact provider keys when the installed Hermes version is uncertain; backend plugin IDs can change across releases.
