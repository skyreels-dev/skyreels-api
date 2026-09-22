# SkyReels API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/bytedance/seedance-2.5?utm_source=github&utm_medium=ugc&utm_campaign=skyreels-dev&utm_content=readme-badge&utm_term=tier-a)

SkyReels-V2 is Skywork AI's open video foundation model built for long clips: it uses diffusion forcing to extend a shot autoregressively instead of stopping at five seconds. This package is a Python client that gives you a SkyReels API for the same job, single-shot videos of up to 30 seconds from a prompt or an image, with `pip install skyreels-api` and no GPU of your own.

You get a blocking `run()` that returns when the video is ready, a submit-and-poll path for queued jobs, webhook delivery for servers that must not block, and one runtime dependency (`requests`). It is meant for content pipelines, backend services and notebooks that need long-form video generation as a function call.

> **Try it now:** [https://synexa.ai/explore/bytedance/seedance-2.5](https://synexa.ai/explore/bytedance/seedance-2.5?utm_source=github&utm_medium=ugc&utm_campaign=skyreels-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About SkyReels](#about-skyreels)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **The 14B checkpoints do not fit consumer cards.** SkyReels-V2's 14B models need well over 40 GB of VRAM for 720p, and the project's multi-GPU path assumes several of them. The hosted endpoint runs on hardware sized for the model.
- **Long clips take a long time locally.** Diffusion-forcing extension generates a 30 second video as a chain of overlapping segments, which on a single GPU means many minutes per clip; a hosted queue lets you fire off dozens in parallel.
- **No cold start.** Loading a 14B diffusion transformer, its text encoder and VAE takes minutes before the first frame; hosted runs start on a warm model.
- **Per-run pricing.** `bytedance/seedance-2.5` is $0.473 per run for up to 30 seconds with audio; `tongyi/wan2.2` image-to-video is $0.20 per 5 second clip. No reserved instance sits idle between jobs.

## Installation

```bash
pip install git+https://github.com/skyreels-dev/skyreels-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=skyreels-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import skyreels_api

output = skyreels_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from skyreels_api import Client

client = Client(api_key="sk-...")
output = client.run({"prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`bytedance/seedance-2.5`](https://synexa.ai/explore/bytedance/seedance-2.5?utm_source=github&utm_medium=ugc&utm_campaign=skyreels-dev&utm_content=readme-models&utm_term=tier-a) | text-to-video | Seedance 2.5 generates a single-shot video of up to 30 seconds from a text prompt, with synchronised audio. | $0.473 |
| [`tongyi/wan2.2`](https://synexa.ai/explore/tongyi/wan2.2?utm_source=github&utm_medium=ugc&utm_campaign=skyreels-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | Generate 5s 480p videos using Wan 2.2 14B. A comprehensive video foundation models that pushes the boundaries of video generation. | $0.2 |

The default model is **`bytedance/seedance-2.5`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `bytedance/seedance-2.5`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A lone fisherman rows out at dawn across…` | — | The text prompt used to generate the video |
| `resolution` | string | no | `720p` | 480p, 720p, 1080p | Video resolution - 480p for faster generation, 720p for balance, 1080p for high quality. |
| `duration` | string | no | `auto` | auto, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 1… | Duration of the video in seconds. Supports 4 to 30 seconds, or auto to let the model decide based on the prompt. |
| `aspect_ratio` | string | no | `auto` | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | The aspect ratio of the generated video. Use 16:9 for landscape, 9:16 for portrait/vertical, 1:1 for square, 21:9 for ultrawide cinematic, or auto to let the model decide. |
| `generate_audio` | boolean | no | `True` | — | Whether to generate synchronized audio for the video, including sound effects, ambient sounds, and lip-synced speech. The cost of video generation is the same regardless of whether audio is generated or not. |
| `bitrate_mode` | string | no | `standard` | standard, high | Output bitrate mode. 'high' requests a higher-quality, larger-file encode from the model; 'standard' uses the default bitrate. |

### `tongyi/wan2.2`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A woman is talking` | — | Input prompt |
| `input_image` | file | yes | `https://files.synexa.ai/models/wan-image…` | — | Input image to start generating from |
| `aspect_ratio` | string | no | `9:16` | 9:16, 1:1, 16:9 | Video Resolution |
| `seed` | integer | no | `random` | — | Random seed. Leave blank to randomize the seed |
| `num_frames` | integer | no | `81` | 1, 81 | Video Frames |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from skyreels_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About SkyReels

SkyReels-V2 was released by Skywork AI in April 2025 as an *infinite-length film generative model*. It combines a structured video captioner (SkyCaptioner-V1) for training data, multi-stage pretraining, reinforcement learning for motion quality, and a diffusion forcing framework in which each frame carries its own noise level, so the model can condition on already-generated frames and keep extending a shot. Checkpoints were published at 1.3B, 5B and 14B parameters, for text-to-video and image-to-video, at 540p and 720p. It follows SkyReels-V1, a human-centric model fine-tuned from HunyuanVideo, and sits alongside SkyReels-A1 and A2 for portrait animation and multi-element composition.

The practical capability is extension: rather than a fixed 5 second output, the diffusion-forcing variants generate a base clip and then continue it segment by segment, with the project demonstrating clips of 30 seconds and longer. A separate camera-director fine-tune adds explicit camera motion control, and the synchronous (non-DF) checkpoints behave like a conventional text- or image-to-video model.

Limits are the usual ones for long autoregressive video: identity and scene details drift as the clip grows, motion can stall in later segments, and 720p 14B generation is slow on a single GPU. The open weights produce silent video; audio has to be added separately.

The hosted endpoint used by this client is `bytedance/seedance-2.5`, which provides the same long single-shot text-to-video capability (4 to 30 seconds, up to 1080p, with synchronised audio); the original SkyReels-V2 weights are available at https://github.com/SkyworkAI/SkyReels-V2 if you want to self-host. For image-to-video the client also exposes `tongyi/wan2.2`, the 14B Wan 2.2 model.

**Official project:** https://github.com/SkyworkAI/SkyReels-V2

## Use cases

- **Long single-shot ads** — call `run()` with a prompt, `duration=20` and `aspect_ratio="16:9"` to get a continuous 20 second product shot with ambient sound.
- **Vertical social clips** — set `aspect_ratio="9:16"` and `resolution="720p"` for reels and shorts, letting `duration="auto"` pick a length that matches the prompt.
- **Animate a key frame** — use the `tongyi/wan2.2` endpoint with a still as `input_image` and a prompt describing the motion to produce a 5 second clip.
- **Dialogue scenes** — keep `generate_audio=True` and write the spoken line in the prompt to get lip-synced speech without a separate TTS pass.
- **Batch previsualisation** — submit one job per storyboard line without blocking and collect the finished videos through a webhook.
- **High-bitrate masters** — request `bitrate_mode="high"` when the clip will be re-encoded downstream and you want the cleanest source.

## FAQ

**Is there a SkyReels API?**

Skywork publishes SkyReels-V2 as open weights and a PyTorch repository, not as a public REST API. This package wraps a hosted Synexa endpoint that provides the same long-form video generation capability, so you can call it over HTTPS without running the model.

**How much does the SkyReels API cost?**

The default endpoint, `bytedance/seedance-2.5`, is $0.473 per run, and that covers any length from 4 to 30 seconds with or without audio. The `tongyi/wan2.2` image-to-video endpoint is $0.20 per 5 second clip. Billing is per completed run.

**Can I run SkyReels without a GPU?**

Not locally; even the 1.3B model needs a CUDA GPU and the 14B models need a large one. With this client the generation happens on the hosted side, so a laptop or a serverless function is enough.

**Does this client work with the original SkyworkAI SkyReels-V2 repo or ComfyUI?**

No. It does not load local checkpoints, run diffusion-forcing inference, or talk to the ComfyUI SkyReels nodes. It is an HTTP client for the hosted endpoints only.

**What input formats does it accept?**

For `bytedance/seedance-2.5` only `prompt` is required; `resolution` (480p, 720p, 1080p), `duration` (4 to 30 seconds or `auto`), `aspect_ratio` (16:9, 9:16, 1:1, 21:9 or `auto`), `generate_audio` and `bitrate_mode` are optional. For `tongyi/wan2.2` you pass a `prompt` and an `input_image`, with optional `aspect_ratio`, `num_frames` and `seed`.

**Is this the official SkyReels SDK?**

No. This is an independent client and is not affiliated with Skywork AI. The official project is at https://github.com/SkyworkAI/SkyReels-V2.

## Related

- [SkyReels-V2 (official repository)](https://github.com/SkyworkAI/SkyReels-V2)
- [Synexa Python client](https://github.com/synexa-ai/synexa-python)
- [bytedance/seedance-2.5 on Synexa](https://synexa.ai/explore/bytedance/seedance-2.5)
- [tongyi/wan2.2 on Synexa](https://synexa.ai/explore/tongyi/wan2.2)

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of SkyReels. Model weights and trademarks belong to their respective owners.

_Last reviewed: 2026-09-22_
