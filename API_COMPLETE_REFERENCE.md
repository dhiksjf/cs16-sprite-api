# ============================================================
#   CS 1.6 SPRITE GENERATOR API — COMPLETE REFERENCE
#   Version 2.0 | Advanced Edition
#   All Endpoints · All Options · All Examples
# ============================================================

## BASE URL
```
http://localhost:8000          # Local
https://your-app.onrender.com  # Production (Render)
https://your-app.railway.app   # Production (Railway)
```

## QUICK LINKS
- Interactive Docs (Swagger) → /docs
- Alternative Docs (ReDoc)   → /redoc
- Features List              → /api/v1/features
- Health Check               → /health

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TABLE OF CONTENTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```
 1. ENDPOINTS OVERVIEW
 2. OPTION REFERENCE (all fields explained)
 3. ENDPOINT: GET  /health
 4. ENDPOINT: GET  /api/v1/features
 5. ENDPOINT: POST /api/v1/convert/image          (basic)
 6. ENDPOINT: POST /api/v1/convert/video          (basic)
 7. ENDPOINT: POST /api/v1/convert/images/animated (basic)
 8. ENDPOINT: POST /api/v2/convert/advanced       ★ STAR
 9. ENDPOINT: GET  /api/v1/download/{sprite_id}
10. ENDPOINT: DELETE /api/v1/delete/{sprite_id}
11. FULL WORKFLOW EXAMPLES
12. LANGUAGE EXAMPLES (Python · JS · cURL · PHP · C#)
13. PRESET CONFIGURATIONS (ready-to-use recipes)
14. RESPONSE FORMAT REFERENCE
15. ERROR CODES REFERENCE
16. DEPLOYMENT CHEATSHEET
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  1. ENDPOINTS OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Method   | Endpoint                             | Description                            |
|----------|--------------------------------------|----------------------------------------|
| GET      | /health                              | Health check                           |
| GET      | /api/v1/features                     | List all available features            |
| POST     | /api/v1/convert/image                | Convert single image → .spr (basic)    |
| POST     | /api/v1/convert/video                | Convert video → .spr (basic)           |
| POST     | /api/v1/convert/images/animated      | Multiple images → animated .spr        |
| POST     | /api/v2/convert/advanced        ★    | Image/video with AI processing         |
| GET      | /api/v1/download/{sprite_id}         | Download the generated .spr file       |
| DELETE   | /api/v1/delete/{sprite_id}           | Delete a generated .spr file           |

★ = Recommended for best quality

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  2. OPTION REFERENCE — ALL FIELDS EXPLAINED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ── SPRITE OPTIONS ──────────────────────────────────────

### sprite_type  (string)
Controls how the sprite orients itself in 3D space.

| Value                  | Description                                    | Best For              |
|------------------------|------------------------------------------------|-----------------------|
| vp_parallel_upright    | Always faces camera, stays upright (DEFAULT)   | Smoke, fire, effects  |
| facing_upright         | Faces player direction, stays upright          | Flames, torches       |
| vp_parallel            | Always faces camera, can freely rotate         | Explosions, sparks    |
| oriented               | Fixed in world space (no billboarding)         | Decals, marks         |
| vp_parallel_oriented   | Faces camera but with custom roll              | Advanced effects      |

### texture_format  (string)
Controls how the sprite blends with the scene.

| Value      | Blending Mode        | Description                                | Best For                    |
|------------|----------------------|--------------------------------------------|-----------------------------|
| additive   | Add to background    | Colors add up — creates glow (DEFAULT)     | Fire, laser, explosions     |
| normal     | Standard             | Standard rendering, color 255 = invisible  | Decals, marks               |
| indexalpha | Alpha from index     | Palette index controls transparency        | Clouds, water effects       |
| alphatest  | Binary transparency  | Pixel is fully visible or fully invisible  | Smoke, sharp-edge sprites   |

### sync_type  (string)
Controls animation start timing when multiple sprite instances exist.

| Value | Description                                        |
|-------|----------------------------------------------------|
| rand  | Random start offset — more natural (DEFAULT)       |
| sync  | All instances start at the same frame              |

### beam_length  (float, default: 0.0)
Length multiplier for beam-type sprites. Only relevant for oriented beam sprites.
Range: 0.0 – ∞

### use_16bit_palette  (bool, default: true)
Include a 256-color RGB palette inside the .spr file.
Always keep this `true` for CS 1.6 compatibility.

### max_width  (int, default: 256)
Maximum width in pixels. Must be a multiple of 8.
Range: 8 – 512. Values auto-rounded down to nearest multiple of 8.

### max_height  (int, default: 256)
Maximum height in pixels. Must be a multiple of 8.
Range: 8 – 512. Values auto-rounded down to nearest multiple of 8.

## ── ADVANCED AI PROCESSING OPTIONS ─────────────────────

### remove_background  (bool, default: false in v1, true in v2)
Activates the background removal engine.
Use with `background_mode` to control how the background is detected.

### background_mode  (string, default: "auto")
Selects which background removal algorithm to use.

| Value   | Algorithm                              | Best For                              |
|---------|----------------------------------------|---------------------------------------|
| auto    | Corner-pixel sampling + flood fill     | Unknown background color              |
| black   | Color distance from (0,0,0)            | Muzzle flashes, fire, explosions      |
| white   | Color distance from (255,255,255)      | Effects on white canvas               |
| green   | HSV-based chroma keying                | Green screen video footage            |
| custom  | Color distance from background_color   | Any specific background color         |
| none    | No background removal                  | Use when background already removed   |

### background_threshold  (int, default: 30)
Color distance tolerance for background removal. Higher = removes more.
Range: 0 – 255
- 10–20 : Very precise, only removes exact match
- 30–50 : Normal tolerance (recommended)
- 60–100: Aggressive removal, may eat into content

### auto_enhance  (bool, default: false)
Enables the auto-enhancement pipeline. Acts as a master switch for the three
enhance_* values below. Must be `true` for individual enhance values to apply.

### enhance_brightness  (float, default: 1.0)
Multiplies the overall brightness of the image.
Range: 0.1 – 3.0
- 0.5 : 50% darker
- 1.0 : No change (identity)
- 1.5 : 50% brighter
- 2.0 : Double brightness

### enhance_contrast  (float, default: 1.0)
Expands or compresses the tonal range.
Range: 0.1 – 3.0
- 0.8 : Lower contrast (washed-out look)
- 1.0 : No change (identity)
- 1.5 : Higher contrast (punchy look)

### enhance_sharpness  (float, default: 1.0)
Controls edge clarity and micro-detail crispness.
Range: 0.1 – 3.0
- 0.0 : Completely blurred
- 1.0 : No change (identity)
- 2.0 : Double sharpness

### auto_crop  (bool, default: false)
Scans the image for content boundaries and crops to fit, removing empty/transparent
regions. Highly recommended to minimize sprite file size.

### crop_padding  (int, default: 5)
Pixel buffer added around content when auto-cropping.
Range: 0 – 50 pixels
- 0  : Tight crop (no padding)
- 5  : Standard padding (recommended)
- 20 : Generous padding

### smooth_edges  (bool, default: false)
Applies Gaussian blur to the alpha channel only — creating smooth, anti-aliased
edges. Does not blur the visible color data.

### edge_blur_radius  (int, default: 2)
Controls how many pixels the edge-smoothing blur spreads.
Range: 1 – 10
- 1–2 : Subtle smoothing
- 3–5 : Moderate anti-aliasing
- 6–10 : Heavy feathering

### denoise  (bool, default: false)
Applies non-local means denoising algorithm (OpenCV). Effective for reducing
compression artifacts, video grain, or scanner noise.

### denoise_strength  (int, default: 5)
Intensity of noise reduction. Higher = more smoothing but may lose detail.
Range: 1 – 20
- 1–5  : Light denoising (keep detail)
- 6–12 : Medium denoising (general use)
- 13–20: Aggressive denoising (heavily noisy sources)

### auto_color_balance  (bool, default: false)
Normalizes each color channel so the image appears neutrally balanced.
Useful when source footage has a color cast (too warm, too cool, etc.).

### gamma_correction  (float, default: 1.0)
Applies a non-linear brightness curve to the image.
Range: 0.1 – 3.0
- 0.5 : Darken midtones
- 1.0 : No change (identity)
- 1.5 : Lift shadows and midtones
- 2.2 : Heavy brightening (simulate sRGB decode)

### center_content  (bool, default: false)
Calculates the center of mass of visible pixels and shifts the image so the
content is perfectly centered in the frame. Ideal for symmetric effects.

### is_video  (bool, default: false)
Used in /api/v2/convert/advanced to tell the API to treat the uploaded file
as a video and extract frames. Must be true for any video input.

### fps  (float, default: 30.0)
Target frames-per-second when extracting from video.
Range: 1 – 60
- 10–15 : Small sprites, basic animation
- 20–24 : Smooth but compact
- 30    : Standard quality
- 60    : Maximum smoothness (large files)

### max_frames  (int, optional)
Hard cap on the number of frames extracted. Prevents gigantic sprites from
long video clips. Not set = no limit.
Recommended: 15–50 for most CS sprites.

### remove_duplicate_frames  (bool, default: false)
Compares adjacent frames and skips those that are too similar, based on
`duplicate_threshold`. Reduces file size without losing animation quality.

### duplicate_threshold  (float, default: 0.95)
Similarity cutoff for duplicate frame removal.
Range: 0.0 – 1.0
- 0.90 : Only remove near-identical frames
- 0.95 : Standard (recommended)
- 0.99 : Very aggressive removal

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  3. GET /health
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check if the API server is alive and advanced features are loaded.

## Request
```
GET /health
```
No parameters required.

## Response
```json
{
  "status": "healthy",
  "advanced_features": true
}
```

## cURL
```bash
curl http://localhost:8000/health
```

## Python
```python
import requests
r = requests.get("http://localhost:8000/health")
print(r.json())
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  4. GET /api/v1/features
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Returns a list of all available features, split by basic and advanced tiers.

## Request
```
GET /api/v1/features
```

## Response
```json
{
  "basic": [
    "Image to sprite conversion",
    "Video to animated sprite",
    "Multiple images to animation",
    "All CS 1.6 sprite types"
  ],
  "advanced": [
    "Automatic background removal",
    "Smart auto-cropping",
    "Image enhancement",
    "Edge smoothing",
    "Noise reduction",
    "Color correction",
    "Content centering",
    "Duplicate frame removal"
  ]
}
```

## cURL
```bash
curl http://localhost:8000/api/v1/features
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  5. POST /api/v1/convert/image   (BASIC)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Convert a single image file to .spr format.
No advanced processing. Fast and simple.

## Accepted Input Formats
PNG · JPG · JPEG · BMP · GIF

## Form Fields
| Field              | Type    | Default                | Required |
|--------------------|---------|------------------------|----------|
| file               | file    | —                      | ✅        |
| sprite_type        | string  | vp_parallel_upright    | ❌        |
| texture_format     | string  | additive               | ❌        |
| sync_type          | string  | rand                   | ❌        |
| beam_length        | float   | 0.0                    | ❌        |
| use_16bit_palette  | bool    | true                   | ❌        |
| max_width          | int     | 256                    | ❌        |
| max_height         | int     | 256                    | ❌        |

## Response
```json
{
  "success": true,
  "message": "Image successfully converted to .spr format",
  "sprite_id": "a3f1c2d4-e5b6-7890-abcd-ef1234567890",
  "filename": "a3f1c2d4-e5b6-7890-abcd-ef1234567890.spr",
  "download_url": "/api/v1/download/a3f1c2d4-e5b6-7890-abcd-ef1234567890",
  "file_size": 8192,
  "frame_count": 1,
  "dimensions": {
    "width": 128,
    "height": 128
  },
  "processing_applied": null
}
```

## Examples

### cURL — Minimal
```bash
curl -X POST "http://localhost:8000/api/v1/convert/image" \
  -F "file=@muzzleflash.png"
```

### cURL — Full Options
```bash
curl -X POST "http://localhost:8000/api/v1/convert/image" \
  -F "file=@muzzleflash.png" \
  -F "sprite_type=vp_parallel" \
  -F "texture_format=additive" \
  -F "sync_type=rand" \
  -F "max_width=128" \
  -F "max_height=128"
```

### Python
```python
import requests

with open("muzzleflash.png", "rb") as f:
    resp = requests.post(
        "http://localhost:8000/api/v1/convert/image",
        files={"file": f},
        data={
            "sprite_type": "vp_parallel",
            "texture_format": "additive",
            "max_width": 128,
            "max_height": 128,
        }
    )

result = resp.json()
print(result["sprite_id"])   # save this to download
```

### JavaScript (fetch)
```javascript
const form = new FormData();
form.append("file", document.querySelector("#fileInput").files[0]);
form.append("texture_format", "additive");
form.append("max_width", "128");

const res = await fetch("/api/v1/convert/image", { method: "POST", body: form });
const data = await res.json();
console.log(data.download_url);
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  6. POST /api/v1/convert/video   (BASIC)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Convert a video file to an animated .spr sprite.
No advanced processing. Use /api/v2/convert/advanced for AI features.

## Accepted Input Formats
MP4 · AVI · MOV · MKV · WEBM

## Form Fields
| Field              | Type    | Default                | Required |
|--------------------|---------|------------------------|----------|
| file               | file    | —                      | ✅        |
| sprite_type        | string  | vp_parallel_upright    | ❌        |
| texture_format     | string  | additive               | ❌        |
| sync_type          | string  | rand                   | ❌        |
| beam_length        | float   | 0.0                    | ❌        |
| use_16bit_palette  | bool    | true                   | ❌        |
| max_width          | int     | 256                    | ❌        |
| max_height         | int     | 256                    | ❌        |
| fps                | float   | 30.0                   | ❌        |
| max_frames         | int     | (no limit)             | ❌        |

## Examples

### cURL — Basic
```bash
curl -X POST "http://localhost:8000/api/v1/convert/video" \
  -F "file=@explosion.mp4" \
  -F "texture_format=additive" \
  -F "fps=20" \
  -F "max_frames=30"
```

### cURL — Full Options
```bash
curl -X POST "http://localhost:8000/api/v1/convert/video" \
  -F "file=@explosion.mp4" \
  -F "sprite_type=vp_parallel" \
  -F "texture_format=additive" \
  -F "fps=15" \
  -F "max_frames=24" \
  -F "max_width=128" \
  -F "max_height=128"
```

### Python
```python
import requests

with open("explosion.mp4", "rb") as f:
    resp = requests.post(
        "http://localhost:8000/api/v1/convert/video",
        files={"file": f},
        data={
            "texture_format": "additive",
            "fps": 20,
            "max_frames": 30,
            "max_width": 128,
            "max_height": 128,
        }
    )

result = resp.json()
print(f"Frames: {result['frame_count']}")
print(f"Download: {result['download_url']}")
```

### Node.js
```javascript
const FormData = require("form-data");
const fs = require("fs");
const axios = require("axios");

const form = new FormData();
form.append("file", fs.createReadStream("explosion.mp4"));
form.append("texture_format", "additive");
form.append("fps", "20");
form.append("max_frames", "30");

const res = await axios.post(
    "http://localhost:8000/api/v1/convert/video",
    form, { headers: form.getHeaders() }
);

console.log(res.data);
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  7. POST /api/v1/convert/images/animated   (BASIC)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Create an animated sprite from multiple image files.
Images are added as frames in the order they are uploaded.

## Accepted Input Formats
PNG · JPG · JPEG · BMP · GIF  (per frame)

## Form Fields
| Field              | Type    | Default                | Required |
|--------------------|---------|------------------------|----------|
| files              | file[]  | —                      | ✅ (1+)   |
| sprite_type        | string  | vp_parallel_upright    | ❌        |
| texture_format     | string  | additive               | ❌        |
| sync_type          | string  | rand                   | ❌        |
| beam_length        | float   | 0.0                    | ❌        |
| use_16bit_palette  | bool    | true                   | ❌        |
| max_width          | int     | 256                    | ❌        |
| max_height         | int     | 256                    | ❌        |
| frame_interval     | float   | 0.1                    | ❌        |

`frame_interval` — time in seconds each frame is displayed (0.1 = 10 FPS)

## Examples

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/convert/images/animated" \
  -F "files=@frame01.png" \
  -F "files=@frame02.png" \
  -F "files=@frame03.png" \
  -F "files=@frame04.png" \
  -F "texture_format=additive" \
  -F "frame_interval=0.05"
```

### Python
```python
import requests

frame_files = ["frame01.png", "frame02.png", "frame03.png", "frame04.png"]
files = [("files", open(p, "rb")) for p in frame_files]

resp = requests.post(
    "http://localhost:8000/api/v1/convert/images/animated",
    files=files,
    data={
        "texture_format": "additive",
        "frame_interval": 0.05,  # 20 FPS
        "max_width": 128,
        "max_height": 128,
    }
)

# Close file handles
for _, fh in files:
    fh.close()

result = resp.json()
print(f"Animated sprite: {result['frame_count']} frames")
```

### Node.js
```javascript
const FormData = require("form-data");
const fs = require("fs");
const axios = require("axios");

const form = new FormData();
["frame01.png", "frame02.png", "frame03.png"].forEach(p => {
    form.append("files", fs.createReadStream(p));
});
form.append("texture_format", "additive");
form.append("frame_interval", "0.05");

const res = await axios.post(
    "http://localhost:8000/api/v1/convert/images/animated",
    form, { headers: form.getHeaders() }
);
console.log(res.data);
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  8. POST /api/v2/convert/advanced   ★ RECOMMENDED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The most powerful endpoint. Accepts both images AND videos.
Applies full AI-powered processing pipeline.

## Accepted Input Formats
Images: PNG · JPG · JPEG · BMP · GIF
Videos: MP4 · AVI · MOV · MKV · WEBM

## ALL Form Fields

### — SPRITE SETTINGS —
| Field              | Type    | Default                | Values                                                                |
|--------------------|---------|------------------------|-----------------------------------------------------------------------|
| file               | file    | —                      | any image or video                                                   |
| sprite_type        | string  | vp_parallel_upright    | vp_parallel_upright · facing_upright · vp_parallel · oriented · vp_parallel_oriented |
| texture_format     | string  | additive               | normal · additive · indexalpha · alphatest                          |
| max_width          | int     | 256                    | 8 – 512 (multiple of 8)                                             |
| max_height         | int     | 256                    | 8 – 512 (multiple of 8)                                             |

### — BACKGROUND REMOVAL —
| Field                  | Type    | Default | Values                                             |
|------------------------|---------|---------|----------------------------------------------------|
| remove_background      | bool    | true    | true · false                                       |
| background_mode        | string  | auto    | auto · black · white · green · custom · none       |
| background_threshold   | int     | 30      | 0 – 255                                            |

### — IMAGE ENHANCEMENT —
| Field                  | Type    | Default | Values   |
|------------------------|---------|---------|----------|
| auto_enhance           | bool    | false   | true/false |
| enhance_brightness     | float   | 1.0     | 0.1 – 3.0 |
| enhance_contrast       | float   | 1.0     | 0.1 – 3.0 |
| enhance_sharpness      | float   | 1.0     | 0.1 – 3.0 |

### — CROPPING & LAYOUT —
| Field                  | Type    | Default | Values   |
|------------------------|---------|---------|----------|
| auto_crop              | bool    | true    | true/false |
| crop_padding           | int     | 5       | 0 – 50   |
| center_content         | bool    | true    | true/false |

### — EDGE & QUALITY —
| Field                  | Type    | Default | Values   |
|------------------------|---------|---------|----------|
| smooth_edges           | bool    | true    | true/false |
| edge_blur_radius       | int     | 2       | 1 – 10   |
| denoise                | bool    | false   | true/false |
| denoise_strength       | int     | 5       | 1 – 20   |

### — COLOR —
| Field                  | Type    | Default | Values     |
|------------------------|---------|---------|------------|
| auto_color_balance     | bool    | false   | true/false |
| gamma_correction       | float   | 1.0     | 0.1 – 3.0  |

### — VIDEO OPTIONS (only when is_video=true) —
| Field                    | Type    | Default | Values     |
|--------------------------|---------|---------|------------|
| is_video                 | bool    | false   | true/false |
| fps                      | float   | 30.0    | 1 – 60     |
| max_frames               | int     | (none)  | 1+         |
| remove_duplicate_frames  | bool    | true    | true/false |
| duplicate_threshold      | float   | 0.95    | 0.0 – 1.0  |

## Response
```json
{
  "success": true,
  "message": "Successfully converted with AI processing",
  "sprite_id": "a3f1c2d4-e5b6-7890-abcd-ef1234567890",
  "filename": "a3f1c2d4-e5b6-7890-abcd-ef1234567890.spr",
  "download_url": "/api/v1/download/a3f1c2d4-e5b6-7890-abcd-ef1234567890",
  "file_size": 32768,
  "frame_count": 20,
  "dimensions": {
    "width": 128,
    "height": 128
  },
  "processing_applied": {
    "background_removal": true,
    "background_mode": "black",
    "auto_enhance": true,
    "auto_crop": true,
    "smooth_edges": true,
    "denoise": false,
    "center_content": true,
    "duplicate_removal": true
  }
}
```

## Examples

### cURL — Image, remove black background
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@muzzleflash.png" \
  -F "remove_background=true" \
  -F "background_mode=black" \
  -F "auto_crop=true" \
  -F "smooth_edges=true" \
  -F "center_content=true" \
  -F "texture_format=additive" \
  -F "max_width=128" \
  -F "max_height=128"
```

### cURL — Image, all enhancements
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@sprite.png" \
  -F "remove_background=true" \
  -F "background_mode=auto" \
  -F "auto_enhance=true" \
  -F "enhance_brightness=1.2" \
  -F "enhance_contrast=1.3" \
  -F "enhance_sharpness=1.4" \
  -F "auto_crop=true" \
  -F "smooth_edges=true" \
  -F "denoise=true" \
  -F "denoise_strength=8" \
  -F "auto_color_balance=true" \
  -F "gamma_correction=1.1" \
  -F "center_content=true" \
  -F "texture_format=additive"
```

### cURL — Green screen video
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@greenscreen.mp4" \
  -F "is_video=true" \
  -F "fps=20" \
  -F "max_frames=40" \
  -F "remove_background=true" \
  -F "background_mode=green" \
  -F "smooth_edges=true" \
  -F "edge_blur_radius=3" \
  -F "remove_duplicate_frames=true" \
  -F "texture_format=alphatest"
```

### cURL — Explosion video, full pipeline
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@explosion.mp4" \
  -F "is_video=true" \
  -F "fps=20" \
  -F "max_frames=30" \
  -F "remove_background=true" \
  -F "background_mode=black" \
  -F "auto_enhance=true" \
  -F "enhance_brightness=1.3" \
  -F "enhance_contrast=1.2" \
  -F "auto_crop=true" \
  -F "smooth_edges=true" \
  -F "denoise=true" \
  -F "center_content=true" \
  -F "remove_duplicate_frames=true" \
  -F "duplicate_threshold=0.95" \
  -F "texture_format=additive" \
  -F "max_width=128" \
  -F "max_height=128"
```

### Python — Full Advanced
```python
import requests

def convert_advanced(file_path, is_video=False, **options):
    """
    Convert image or video to .spr with full AI processing.
    
    Example:
        result = convert_advanced("explosion.mp4", is_video=True, fps=20)
        result = convert_advanced("muzzle.png", background_mode="black")
    """
    defaults = {
        # Sprite
        "sprite_type": "vp_parallel",
        "texture_format": "additive",
        "max_width": 128,
        "max_height": 128,
        # Background
        "remove_background": True,
        "background_mode": "black",
        "background_threshold": 30,
        # Enhancement
        "auto_enhance": False,
        "enhance_brightness": 1.0,
        "enhance_contrast": 1.0,
        "enhance_sharpness": 1.0,
        # Processing
        "auto_crop": True,
        "crop_padding": 5,
        "smooth_edges": True,
        "edge_blur_radius": 2,
        "denoise": False,
        "denoise_strength": 5,
        "auto_color_balance": False,
        "gamma_correction": 1.0,
        "center_content": True,
        # Video
        "is_video": is_video,
        "fps": 20.0,
        "max_frames": 30,
        "remove_duplicate_frames": True,
        "duplicate_threshold": 0.95,
    }
    defaults.update(options)

    with open(file_path, "rb") as f:
        resp = requests.post(
            "http://localhost:8000/api/v2/convert/advanced",
            files={"file": f},
            data=defaults
        )

    if resp.status_code == 200:
        result = resp.json()
        print(f"✅ {result['frame_count']} frame(s), {result['file_size']} bytes")
        return result
    else:
        raise Exception(f"Error {resp.status_code}: {resp.text}")


def download_sprite(sprite_id, output_path="output.spr"):
    """Download the generated sprite file."""
    resp = requests.get(
        f"http://localhost:8000/api/v1/download/{sprite_id}",
        stream=True
    )
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    print(f"💾 Saved to: {output_path}")


# ── Usage Examples ────────────────────────────────────────

# Muzzle flash (black bg removal)
result = convert_advanced("muzzleflash.png", background_mode="black")
download_sprite(result["sprite_id"], "muzzleflash.spr")

# Explosion video
result = convert_advanced(
    "explosion.mp4",
    is_video=True,
    fps=20,
    max_frames=30,
    auto_enhance=True,
    enhance_brightness=1.3,
)
download_sprite(result["sprite_id"], "explosion.spr")

# Green screen
result = convert_advanced(
    "greenscreen.mp4",
    is_video=True,
    background_mode="green",
    texture_format="alphatest",
)
download_sprite(result["sprite_id"], "effect.spr")
```

### JavaScript / Node.js — Advanced
```javascript
const FormData = require("form-data");
const fs = require("fs");
const axios = require("axios");

async function convertAdvanced(filePath, isVideo = false, options = {}) {
    const defaults = {
        sprite_type: "vp_parallel",
        texture_format: "additive",
        max_width: "128",
        max_height: "128",
        remove_background: "true",
        background_mode: "black",
        background_threshold: "30",
        auto_enhance: "false",
        enhance_brightness: "1.0",
        enhance_contrast: "1.0",
        enhance_sharpness: "1.0",
        auto_crop: "true",
        smooth_edges: "true",
        edge_blur_radius: "2",
        denoise: "false",
        center_content: "true",
        is_video: String(isVideo),
        fps: "20",
        max_frames: "30",
        remove_duplicate_frames: "true",
        duplicate_threshold: "0.95",
        ...options,
    };

    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));
    Object.entries(defaults).forEach(([k, v]) => form.append(k, v));

    const res = await axios.post(
        "http://localhost:8000/api/v2/convert/advanced",
        form,
        { headers: form.getHeaders() }
    );

    return res.data;
}

async function downloadSprite(spriteId, outputPath = "output.spr") {
    const res = await axios.get(
        `http://localhost:8000/api/v1/download/${spriteId}`,
        { responseType: "arraybuffer" }
    );
    fs.writeFileSync(outputPath, res.data);
    console.log(`Saved to: ${outputPath}`);
}

// Usage
const result = await convertAdvanced("muzzleflash.png");
await downloadSprite(result.sprite_id, "muzzleflash.spr");

const videoResult = await convertAdvanced("explosion.mp4", true, { fps: "20" });
await downloadSprite(videoResult.sprite_id, "explosion.spr");
```

### PHP — Advanced
```php
<?php
function convertAdvanced($filePath, $isVideo = false, $options = []) {
    $defaults = [
        "sprite_type"             => "vp_parallel",
        "texture_format"          => "additive",
        "max_width"               => 128,
        "max_height"              => 128,
        "remove_background"       => "true",
        "background_mode"         => "black",
        "background_threshold"    => 30,
        "auto_enhance"            => "false",
        "auto_crop"               => "true",
        "smooth_edges"            => "true",
        "center_content"          => "true",
        "is_video"                => $isVideo ? "true" : "false",
        "fps"                     => 20,
        "max_frames"              => 30,
        "remove_duplicate_frames" => "true",
    ];
    $params = array_merge($defaults, $options);
    $params["file"] = new CURLFile($filePath);

    $ch = curl_init("http://localhost:8000/api/v2/convert/advanced");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $params);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    curl_close($ch);

    return json_decode($response, true);
}

$result = convertAdvanced("muzzleflash.png");
$spriteId = $result["sprite_id"];

// Download
file_put_contents(
    "output.spr",
    file_get_contents("http://localhost:8000/api/v1/download/$spriteId")
);
?>
```

### C# — Advanced
```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;

class SpriteClient {
    private static readonly HttpClient _http = new HttpClient();
    private static readonly string Base = "http://localhost:8000";

    public static async Task<JsonElement> ConvertAdvanced(
        string filePath, bool isVideo = false) {

        using var form = new MultipartFormDataContent();
        form.Add(new ByteArrayContent(File.ReadAllBytes(filePath)),
                 "file", Path.GetFileName(filePath));

        form.Add(new StringContent("vp_parallel"),  "sprite_type");
        form.Add(new StringContent("additive"),      "texture_format");
        form.Add(new StringContent("128"),           "max_width");
        form.Add(new StringContent("128"),           "max_height");
        form.Add(new StringContent("true"),          "remove_background");
        form.Add(new StringContent("black"),         "background_mode");
        form.Add(new StringContent("true"),          "auto_crop");
        form.Add(new StringContent("true"),          "smooth_edges");
        form.Add(new StringContent("true"),          "center_content");
        form.Add(new StringContent(isVideo.ToString().ToLower()), "is_video");
        form.Add(new StringContent("20"),            "fps");
        form.Add(new StringContent("30"),            "max_frames");
        form.Add(new StringContent("true"),          "remove_duplicate_frames");

        var response = await _http.PostAsync($"{Base}/api/v2/convert/advanced", form);
        var json = await response.Content.ReadAsStringAsync();
        return JsonDocument.Parse(json).RootElement;
    }

    public static async Task DownloadSprite(string spriteId, string outputPath) {
        var bytes = await _http.GetByteArrayAsync(
            $"{Base}/api/v1/download/{spriteId}");
        await File.WriteAllBytesAsync(outputPath, bytes);
        Console.WriteLine($"Saved: {outputPath}");
    }
}

// Usage
var result = await SpriteClient.ConvertAdvanced("muzzleflash.png");
var spriteId = result.GetProperty("sprite_id").GetString();
await SpriteClient.DownloadSprite(spriteId, "muzzleflash.spr");
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  9. GET /api/v1/download/{sprite_id}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Download the binary .spr file after conversion.

## Path Parameters
| Param      | Type   | Description                                        |
|------------|--------|----------------------------------------------------|
| sprite_id  | string | UUID returned by any convert endpoint              |

## Response
Binary stream, Content-Type: `application/octet-stream`
Content-Disposition: `attachment; filename="<sprite_id>.spr"`

## Examples

### cURL — Save with custom name
```bash
curl -o "my_sprite.spr" \
  "http://localhost:8000/api/v1/download/a3f1c2d4-e5b6-7890-abcd-ef1234567890"
```

### cURL — Save with server filename
```bash
curl -O -J \
  "http://localhost:8000/api/v1/download/a3f1c2d4-e5b6-7890-abcd-ef1234567890"
```

### Python
```python
import requests

def download_sprite(sprite_id, output_name=None):
    resp = requests.get(
        f"http://localhost:8000/api/v1/download/{sprite_id}",
        stream=True
    )
    if resp.status_code == 200:
        fname = output_name or f"{sprite_id}.spr"
        with open(fname, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {fname}")
    else:
        print(f"Error: {resp.status_code}")

download_sprite("a3f1c2d4-e5b6-7890-abcd-ef1234567890", "explosion.spr")
```

### JavaScript (browser)
```javascript
async function downloadSprite(spriteId, fileName = "sprite.spr") {
    const res = await fetch(`/api/v1/download/${spriteId}`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
}
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. DELETE /api/v1/delete/{sprite_id}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Remove a generated .spr file from the server.
Call this after downloading to free up disk space.

## Path Parameters
| Param      | Type   | Description                |
|------------|--------|----------------------------|
| sprite_id  | string | UUID of the sprite to delete |

## Response
```json
{
  "success": true,
  "message": "Sprite deleted successfully"
}
```

## Examples

### cURL
```bash
curl -X DELETE \
  "http://localhost:8000/api/v1/delete/a3f1c2d4-e5b6-7890-abcd-ef1234567890"
```

### Python (full workflow: convert → download → delete)
```python
import requests

BASE = "http://localhost:8000"

def full_workflow(image_path, output_path):
    """Convert, download, then clean up."""
    # 1. Convert
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{BASE}/api/v2/convert/advanced",
            files={"file": f},
            data={"remove_background": True, "background_mode": "black"}
        )
    result = resp.json()
    sprite_id = result["sprite_id"]
    print(f"Converted: {result['frame_count']} frames")

    # 2. Download
    dl = requests.get(f"{BASE}/api/v1/download/{sprite_id}", stream=True)
    with open(output_path, "wb") as f:
        for chunk in dl.iter_content(8192):
            f.write(chunk)
    print(f"Downloaded: {output_path}")

    # 3. Delete from server
    requests.delete(f"{BASE}/api/v1/delete/{sprite_id}")
    print("Cleaned up server.")

full_workflow("muzzleflash.png", "muzzleflash.spr")
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 11. FULL WORKFLOW EXAMPLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ── Workflow A: Muzzle Flash (Black Background) ──────────
```bash
# Step 1: Convert
RESULT=$(curl -s -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@muzzleflash.png" \
  -F "remove_background=true" \
  -F "background_mode=black" \
  -F "auto_crop=true" \
  -F "smooth_edges=true" \
  -F "center_content=true" \
  -F "texture_format=additive" \
  -F "max_width=128" \
  -F "max_height=128")

# Step 2: Extract sprite_id (requires jq)
SPRITE_ID=$(echo $RESULT | jq -r '.sprite_id')
echo "Sprite ID: $SPRITE_ID"

# Step 3: Download
curl -o "muzzleflash.spr" \
  "http://localhost:8000/api/v1/download/$SPRITE_ID"

# Step 4: Clean up
curl -X DELETE "http://localhost:8000/api/v1/delete/$SPRITE_ID"
echo "Done! Copy muzzleflash.spr to your CS 1.6 sprites folder."
```

## ── Workflow B: Explosion Video ─────────────────────────
```python
import requests

BASE = "http://localhost:8000"

# Step 1: Convert video
with open("explosion.mp4", "rb") as f:
    resp = requests.post(f"{BASE}/api/v2/convert/advanced",
        files={"file": f},
        data={
            "is_video": True,
            "fps": 20,
            "max_frames": 30,
            "remove_background": True,
            "background_mode": "black",
            "background_threshold": 40,
            "auto_enhance": True,
            "enhance_brightness": 1.2,
            "enhance_contrast": 1.3,
            "auto_crop": True,
            "smooth_edges": True,
            "edge_blur_radius": 2,
            "denoise": True,
            "denoise_strength": 5,
            "center_content": True,
            "remove_duplicate_frames": True,
            "duplicate_threshold": 0.95,
            "texture_format": "additive",
            "max_width": 256,
            "max_height": 256,
        }
    )

result = resp.json()
print(f"Created {result['frame_count']} frames, {result['file_size']} bytes")

# Step 2: Download
dl = requests.get(f"{BASE}/api/v1/download/{result['sprite_id']}", stream=True)
with open("explosion.spr", "wb") as f:
    for chunk in dl.iter_content(8192):
        f.write(chunk)

print("explosion.spr ready for CS 1.6!")
```

## ── Workflow C: Green Screen Effect ─────────────────────
```python
import requests

BASE = "http://localhost:8000"

with open("greenscreen_effect.mp4", "rb") as f:
    resp = requests.post(f"{BASE}/api/v2/convert/advanced",
        files={"file": f},
        data={
            "is_video": True,
            "fps": 24,
            "max_frames": 48,
            "remove_background": True,
            "background_mode": "green",
            "smooth_edges": True,
            "edge_blur_radius": 3,
            "auto_crop": True,
            "remove_duplicate_frames": True,
            "texture_format": "alphatest",
            "max_width": 256,
            "max_height": 256,
        }
    )

result = resp.json()
dl = requests.get(f"{BASE}/api/v1/download/{result['sprite_id']}", stream=True)
with open("greenscreen.spr", "wb") as f:
    for chunk in dl.iter_content(8192):
        f.write(chunk)
print("greenscreen.spr ready!")
```

## ── Workflow D: Batch Convert a Folder ──────────────────
```python
import requests
import os
from pathlib import Path

BASE = "http://localhost:8000"
INPUT_DIR = Path("./sprites_input")
OUTPUT_DIR = Path("./sprites_output")
OUTPUT_DIR.mkdir(exist_ok=True)

results = []
for image_path in INPUT_DIR.glob("*.png"):
    print(f"Processing: {image_path.name}")
    with open(image_path, "rb") as f:
        resp = requests.post(f"{BASE}/api/v2/convert/advanced",
            files={"file": f},
            data={
                "remove_background": True,
                "background_mode": "black",
                "auto_crop": True,
                "smooth_edges": True,
                "texture_format": "additive",
            }
        )

    if resp.status_code == 200:
        result = resp.json()
        sprite_id = result["sprite_id"]
        output_name = OUTPUT_DIR / f"{image_path.stem}.spr"

        # Download
        dl = requests.get(f"{BASE}/api/v1/download/{sprite_id}", stream=True)
        with open(output_name, "wb") as f:
            for chunk in dl.iter_content(8192):
                f.write(chunk)

        # Delete from server
        requests.delete(f"{BASE}/api/v1/delete/{sprite_id}")

        results.append({"input": image_path.name, "output": str(output_name)})
        print(f"  ✅ {output_name.name}")
    else:
        print(f"  ❌ Failed: {resp.text}")

print(f"\nDone! Converted {len(results)} sprites.")
```

## ── Workflow E: Animated Sprite from Image Sequence ─────
```python
import requests

BASE = "http://localhost:8000"

frame_paths = sorted(Path("./frames").glob("frame_*.png"))

files = [("files", open(p, "rb")) for p in frame_paths]
try:
    resp = requests.post(f"{BASE}/api/v1/convert/images/animated",
        files=files,
        data={
            "texture_format": "additive",
            "frame_interval": 0.05,   # 20 FPS
            "max_width": 128,
            "max_height": 128,
        }
    )
finally:
    for _, fh in files:
        fh.close()

result = resp.json()
dl = requests.get(f"{BASE}/api/v1/download/{result['sprite_id']}", stream=True)
with open("animation.spr", "wb") as f:
    for chunk in dl.iter_content(8192):
        f.write(chunk)

print(f"animation.spr: {result['frame_count']} frames @ 20 FPS")
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 12. LANGUAGE EXAMPLES (ALL ENDPOINTS SIDE BY SIDE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ── PYTHON (requests library) ────────────────────────────

```python
import requests

BASE = "http://localhost:8000"

# Health check
requests.get(f"{BASE}/health").json()

# Features
requests.get(f"{BASE}/api/v1/features").json()

# Convert image (basic)
with open("img.png","rb") as f:
    r = requests.post(f"{BASE}/api/v1/convert/image",
        files={"file": f}, data={"texture_format": "additive"})

# Convert video (basic)
with open("vid.mp4","rb") as f:
    r = requests.post(f"{BASE}/api/v1/convert/video",
        files={"file": f}, data={"fps": 20, "max_frames": 30})

# Convert multiple images
files = [("files", open(p,"rb")) for p in ["a.png","b.png","c.png"]]
r = requests.post(f"{BASE}/api/v1/convert/images/animated",
    files=files, data={"frame_interval": 0.1})
for _,f in files: f.close()

# Advanced conversion (image)
with open("img.png","rb") as f:
    r = requests.post(f"{BASE}/api/v2/convert/advanced",
        files={"file": f},
        data={"remove_background":True, "background_mode":"black",
              "auto_crop":True, "smooth_edges":True})

# Advanced conversion (video)
with open("vid.mp4","rb") as f:
    r = requests.post(f"{BASE}/api/v2/convert/advanced",
        files={"file": f},
        data={"is_video":True, "fps":20, "max_frames":30,
              "remove_background":True, "remove_duplicate_frames":True})

sprite_id = r.json()["sprite_id"]

# Download
dl = requests.get(f"{BASE}/api/v1/download/{sprite_id}", stream=True)
with open("out.spr","wb") as f:
    for chunk in dl.iter_content(8192): f.write(chunk)

# Delete
requests.delete(f"{BASE}/api/v1/delete/{sprite_id}")
```

## ── JAVASCRIPT / NODE.JS ─────────────────────────────────

```javascript
const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");
const BASE = "http://localhost:8000";

// Helper: build form from file path + data object
function buildForm(filePath, data = {}) {
    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));
    Object.entries(data).forEach(([k, v]) => form.append(k, String(v)));
    return form;
}

// Health
await axios.get(`${BASE}/health`);

// Features
await axios.get(`${BASE}/api/v1/features`);

// Convert image
const form1 = buildForm("img.png", { texture_format: "additive" });
const res1 = await axios.post(`${BASE}/api/v1/convert/image`,
    form1, { headers: form1.getHeaders() });

// Convert video
const form2 = buildForm("vid.mp4", { fps: 20, max_frames: 30 });
const res2 = await axios.post(`${BASE}/api/v1/convert/video`,
    form2, { headers: form2.getHeaders() });

// Advanced
const form3 = buildForm("img.png", {
    remove_background: true,
    background_mode: "black",
    auto_crop: true,
    smooth_edges: true,
});
const res3 = await axios.post(`${BASE}/api/v2/convert/advanced`,
    form3, { headers: form3.getHeaders() });

const { sprite_id } = res3.data;

// Download
const dl = await axios.get(`${BASE}/api/v1/download/${sprite_id}`,
    { responseType: "arraybuffer" });
fs.writeFileSync("out.spr", dl.data);

// Delete
await axios.delete(`${BASE}/api/v1/delete/${sprite_id}`);
```

## ── JAVASCRIPT (BROWSER / FETCH) ────────────────────────

```javascript
const BASE = "http://localhost:8000";

// Health
const health = await fetch(`${BASE}/health`).then(r => r.json());

// Convert image from <input type="file">
async function convertImage(fileInput) {
    const form = new FormData();
    form.append("file", fileInput.files[0]);
    form.append("texture_format", "additive");
    form.append("remove_background", "true");
    form.append("background_mode", "black");

    const res = await fetch(`${BASE}/api/v2/convert/advanced`,
        { method: "POST", body: form });
    return res.json();
}

// Download sprite as browser download
async function downloadSprite(spriteId, name = "sprite.spr") {
    const res = await fetch(`${BASE}/api/v1/download/${spriteId}`);
    const blob = await res.blob();
    const a = Object.assign(document.createElement("a"), {
        href: URL.createObjectURL(blob),
        download: name
    });
    a.click();
}
```

## ── cURL ─────────────────────────────────────────────────

```bash
BASE="http://localhost:8000"

# Health
curl "$BASE/health"

# Features
curl "$BASE/api/v1/features"

# Convert image (minimal)
curl -X POST "$BASE/api/v1/convert/image" -F "file=@img.png"

# Convert image (full options)
curl -X POST "$BASE/api/v1/convert/image" \
  -F "file=@img.png" -F "sprite_type=vp_parallel" \
  -F "texture_format=additive" -F "max_width=128" -F "max_height=128"

# Convert video
curl -X POST "$BASE/api/v1/convert/video" \
  -F "file=@vid.mp4" -F "fps=20" -F "max_frames=30"

# Convert multiple images
curl -X POST "$BASE/api/v1/convert/images/animated" \
  -F "files=@frame1.png" -F "files=@frame2.png" \
  -F "frame_interval=0.1"

# Advanced image
curl -X POST "$BASE/api/v2/convert/advanced" \
  -F "file=@img.png" -F "remove_background=true" \
  -F "background_mode=black" -F "auto_crop=true" \
  -F "smooth_edges=true" -F "center_content=true"

# Advanced video
curl -X POST "$BASE/api/v2/convert/advanced" \
  -F "file=@vid.mp4" -F "is_video=true" \
  -F "fps=20" -F "max_frames=30" \
  -F "remove_background=true" -F "remove_duplicate_frames=true"

# Download
SPRITE_ID="your-uuid-here"
curl -o "output.spr" "$BASE/api/v1/download/$SPRITE_ID"

# Delete
curl -X DELETE "$BASE/api/v1/delete/$SPRITE_ID"
```

## ── PHP ──────────────────────────────────────────────────

```php
<?php
$BASE = "http://localhost:8000";

function curlRequest($method, $url, $postFields = null) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    if ($method === "POST") {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
    } elseif ($method === "DELETE") {
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "DELETE");
    }
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

// Advanced image conversion
$result = curlRequest("POST", "$BASE/api/v2/convert/advanced", [
    "file"                => new CURLFile("img.png"),
    "remove_background"   => "true",
    "background_mode"     => "black",
    "auto_crop"           => "true",
    "smooth_edges"        => "true",
    "texture_format"      => "additive",
]);

$spriteId = $result["sprite_id"];

// Download
file_put_contents("output.spr",
    file_get_contents("$BASE/api/v1/download/$spriteId"));

// Delete
curlRequest("DELETE", "$BASE/api/v1/delete/$spriteId");
?>
```

## ── C# ───────────────────────────────────────────────────

```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;

class SpriteApiClient {
    private readonly HttpClient _http = new();
    private readonly string _base;

    public SpriteApiClient(string baseUrl = "http://localhost:8000")
        => _base = baseUrl;

    // Shared helper to build multipart form
    MultipartFormDataContent BuildForm(string filePath, object options) {
        var form = new MultipartFormDataContent();
        form.Add(new ByteArrayContent(File.ReadAllBytes(filePath)),
                 "file", Path.GetFileName(filePath));
        foreach (var prop in options.GetType().GetProperties())
            form.Add(new StringContent(prop.GetValue(options)?.ToString() ?? ""),
                     prop.Name);
        return form;
    }

    // Convert advanced
    public async Task<string> ConvertAdvanced(string filePath, bool isVideo = false) {
        using var form = new MultipartFormDataContent();
        form.Add(new ByteArrayContent(File.ReadAllBytes(filePath)),
                 "file", Path.GetFileName(filePath));
        form.Add(new StringContent("additive"),        "texture_format");
        form.Add(new StringContent("vp_parallel"),     "sprite_type");
        form.Add(new StringContent("128"),             "max_width");
        form.Add(new StringContent("128"),             "max_height");
        form.Add(new StringContent("true"),            "remove_background");
        form.Add(new StringContent("black"),           "background_mode");
        form.Add(new StringContent("true"),            "auto_crop");
        form.Add(new StringContent("true"),            "smooth_edges");
        form.Add(new StringContent("true"),            "center_content");
        form.Add(new StringContent(isVideo?"true":"false"), "is_video");
        form.Add(new StringContent("20"),              "fps");
        form.Add(new StringContent("30"),              "max_frames");
        form.Add(new StringContent("true"),            "remove_duplicate_frames");

        var resp = await _http.PostAsync($"{_base}/api/v2/convert/advanced", form);
        var json = JsonDocument.Parse(await resp.Content.ReadAsStringAsync());
        return json.RootElement.GetProperty("sprite_id").GetString()!;
    }

    // Download
    public async Task Download(string spriteId, string outputPath) {
        var bytes = await _http.GetByteArrayAsync(
            $"{_base}/api/v1/download/{spriteId}");
        await File.WriteAllBytesAsync(outputPath, bytes);
    }

    // Delete
    public async Task Delete(string spriteId) =>
        await _http.DeleteAsync($"{_base}/api/v1/delete/{spriteId}");
}

// Usage
var client = new SpriteApiClient();
var id = await client.ConvertAdvanced("muzzleflash.png");
await client.Download(id, "muzzleflash.spr");
await client.Delete(id);
Console.WriteLine("Done!");
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 13. PRESET CONFIGURATIONS (READY-TO-USE RECIPES)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ── 🔫 Muzzle Flash ──────────────────────────────────────
```
texture_format      = additive
sprite_type         = vp_parallel
max_width           = 128
max_height          = 128
remove_background   = true
background_mode     = black
background_threshold= 30
auto_crop           = true
smooth_edges        = true
center_content      = true
```
```bash
curl -X POST ".../api/v2/convert/advanced" -F "file=@muzzle.png" \
  -F "texture_format=additive" -F "sprite_type=vp_parallel" \
  -F "remove_background=true" -F "background_mode=black" \
  -F "auto_crop=true" -F "smooth_edges=true" -F "center_content=true" \
  -F "max_width=128" -F "max_height=128"
```

## ── 💥 Explosion (Image) ─────────────────────────────────
```
texture_format      = additive
sprite_type         = vp_parallel
max_width           = 256
max_height          = 256
remove_background   = true
background_mode     = black
auto_enhance        = true
enhance_brightness  = 1.3
enhance_contrast    = 1.2
auto_crop           = true
smooth_edges        = true
center_content      = true
```

## ── 🎬 Explosion (Video) ─────────────────────────────────
```
is_video                = true
fps                     = 20
max_frames              = 30
texture_format          = additive
sprite_type             = vp_parallel
max_width               = 256
max_height              = 256
remove_background       = true
background_mode         = black
background_threshold    = 40
auto_enhance            = true
enhance_brightness      = 1.2
enhance_contrast        = 1.3
denoise                 = true
denoise_strength        = 5
auto_crop               = true
smooth_edges            = true
center_content          = true
remove_duplicate_frames = true
duplicate_threshold     = 0.95
```

## ── 💨 Smoke Effect ──────────────────────────────────────
```
texture_format      = alphatest
sprite_type         = facing_upright
max_width           = 128
max_height          = 128
remove_background   = true
background_mode     = auto
smooth_edges        = true
edge_blur_radius    = 4
auto_crop           = true
```

## ── 🌿 Green Screen Video ────────────────────────────────
```
is_video                = true
fps                     = 24
max_frames              = 48
texture_format          = alphatest
sprite_type             = vp_parallel
max_width               = 256
max_height              = 256
remove_background       = true
background_mode         = green
smooth_edges            = true
edge_blur_radius        = 3
auto_crop               = true
remove_duplicate_frames = true
```

## ── 🩸 Blood Splatter ────────────────────────────────────
```
texture_format      = normal
sprite_type         = oriented
max_width           = 64
max_height          = 64
remove_background   = true
background_mode     = white
auto_crop           = true
smooth_edges        = true
```

## ── ⚡ Laser / Beam ──────────────────────────────────────
```
texture_format      = additive
sprite_type         = oriented
beam_length         = 128.0
max_width           = 16
max_height          = 16
```

## ── 🔥 Fire / Flame ──────────────────────────────────────
```
texture_format          = additive
sprite_type             = facing_upright
max_width               = 64
max_height              = 128
is_video                = true
fps                     = 15
max_frames              = 20
remove_background       = true
background_mode         = black
auto_enhance            = true
enhance_brightness      = 1.1
remove_duplicate_frames = false
smooth_edges            = true
```

## ── 💫 Particle / Spark ──────────────────────────────────
```
texture_format      = additive
sprite_type         = vp_parallel
max_width           = 32
max_height          = 32
remove_background   = true
background_mode     = black
auto_crop           = true
center_content      = true
smooth_edges        = true
```

## ── 📷 Scanned Image Cleanup ─────────────────────────────
```
denoise             = true
denoise_strength    = 12
auto_enhance        = true
enhance_contrast    = 1.4
enhance_sharpness   = 1.6
auto_crop           = true
auto_color_balance  = true
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 14. RESPONSE FORMAT REFERENCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Standard Success Response (all convert endpoints)
```json
{
  "success": true,
  "message": "Successfully converted with AI processing",
  "sprite_id": "UUID string — use this to download or delete",
  "filename": "UUID.spr — name on server",
  "download_url": "/api/v1/download/UUID — full path for download",
  "file_size": 32768,    // bytes
  "frame_count": 20,     // number of frames in sprite
  "dimensions": {
    "width": 128,        // max frame width in pixels
    "height": 128        // max frame height in pixels
  },
  "processing_applied": {    // only in v2 endpoint
    "background_removal": true,
    "background_mode": "black",
    "auto_enhance": true,
    "auto_crop": true,
    "smooth_edges": true,
    "denoise": false,
    "center_content": true,
    "duplicate_removal": true
  }
}
```

## Standard Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Health Response
```json
{
  "status": "healthy",
  "advanced_features": true
}
```

## Delete Response
```json
{
  "success": true,
  "message": "Sprite deleted successfully"
}
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 15. ERROR CODES REFERENCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| HTTP Status | Meaning                          | Common Causes                                    |
|-------------|----------------------------------|--------------------------------------------------|
| 200         | OK                               | Success                                          |
| 400         | Bad Request                      | Unsupported file type, invalid parameters        |
| 404         | Not Found                        | sprite_id doesn't exist (wrong ID or deleted)    |
| 422         | Unprocessable Entity             | Missing required fields, type mismatch           |
| 500         | Internal Server Error            | Corrupt file, processing failure, out of memory  |
| 501         | Not Implemented                  | Advanced features unavailable (missing opencv)   |

### Common Error Messages and Fixes

| Error                                            | Fix                                              |
|--------------------------------------------------|--------------------------------------------------|
| "Unsupported file type"                          | Use PNG, JPG, BMP, GIF for images; MP4/AVI for videos |
| "Advanced features not available"               | Install opencv: `pip install opencv-python`      |
| "No frames extracted from video"                | Check video file is valid; try lower fps         |
| "Sprite not found"                              | sprite_id is wrong or already deleted            |
| "Failed to open video"                          | Video codec unsupported; convert to mp4 first    |
| "No valid image files provided"                 | All uploaded files were wrong format             |
| 422 on boolean field                            | Use string "true"/"false" in form data, not bool |

### Note on Boolean Values in Form Data
When sending form data (not JSON), booleans must be strings:
```bash
# CORRECT in form data:
-F "remove_background=true"
-F "is_video=true"

# CORRECT in Python requests data={} dict:
data={"remove_background": True}   # requests handles this automatically
data={"remove_background": "true"} # also works
```

---

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 16. DEPLOYMENT CHEATSHEET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ── Local Docker ─────────────────────────────────────────
```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up --build --force-recreate
```

## ── Render.com ───────────────────────────────────────────
```
1. Push code to GitHub
2. New Web Service → Connect repo
3. Environment: Docker
4. Port: 8000
5. (Optional) Add Disk: /app/outputs, 1GB
6. Deploy
URL: https://your-app.onrender.com
```

## ── Railway.app ──────────────────────────────────────────
```bash
npm install -g @railway/cli
railway login
railway init
railway up
railway domain   # get URL
```

## ── Fly.io ───────────────────────────────────────────────
```bash
fly launch                      # configure
fly deploy                      # deploy
fly open                        # open in browser
fly logs                        # view logs
fly scale memory 1024           # increase RAM if needed
```

## ── Docker (Any Host) ───────────────────────────────────
```bash
# Build
docker build -t sprite-api .

# Run (with persistent storage)
docker run -d \
  -p 8000:8000 \
  -v ./outputs:/app/outputs \
  -v ./temp:/app/temp \
  --name sprite-api \
  --restart unless-stopped \
  sprite-api

# Check status
docker ps
docker logs sprite-api

# Stop/remove
docker stop sprite-api
docker rm sprite-api
```

## ── Environment Variables ────────────────────────────────
```bash
PORT=8000           # Server port (default: 8000)
HOST=0.0.0.0        # Bind address (default: 0.0.0.0)
```

## ── Health Check After Deploy ────────────────────────────
```bash
curl https://your-deployed-url.com/health
# Expected: {"status":"healthy","advanced_features":true}
```

---

# ============================================================
#   END OF REFERENCE
#   CS 1.6 Sprite Generator API v2.0 — Advanced Edition
# ============================================================
