# CS 1.6 Sprite Generator API

A production-ready REST API for converting images and videos to Counter-Strike 1.6 `.spr` sprite format. Built with FastAPI and Docker for easy deployment on platforms like Render, Railway, Fly.io, or any Docker-compatible hosting service.

## Features

- ✅ Convert single images to `.spr` format
- ✅ Convert videos to animated `.spr` sprites
- ✅ Create animated sprites from multiple images
- ✅ Fully customizable sprite options (type, texture format, dimensions)
- ✅ RESTful JSON API
- ✅ Docker support for easy deployment
- ✅ Production-ready with health checks
- ✅ CORS enabled for web applications
- ✅ Automatic file cleanup

## Supported Formats

### Input
- **Images**: PNG, JPG, JPEG, BMP, GIF
- **Videos**: MP4, AVI, MOV, MKV, WEBM

### Output
- **Sprite**: `.spr` (CS 1.6 compatible)

## API Endpoints

### 1. Convert Single Image
**POST** `/api/v1/convert/image`

Convert a single image to `.spr` format.

**Form Parameters:**
- `file` (required): Image file
- `sprite_type` (optional): `vp_parallel_upright`, `facing_upright`, `vp_parallel`, `oriented`, `vp_parallel_oriented`
- `texture_format` (optional): `normal`, `additive`, `indexalpha`, `alphatest`
- `sync_type` (optional): `sync`, `rand`
- `beam_length` (optional): Float, default 0.0
- `use_16bit_palette` (optional): Boolean, default true
- `max_width` (optional): Integer (8-512), default 256
- `max_height` (optional): Integer (8-512), default 256

**Response:**
```json
{
  "success": true,
  "message": "Image successfully converted to .spr format",
  "sprite_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "550e8400-e29b-41d4-a716-446655440000.spr",
  "download_url": "/api/v1/download/550e8400-e29b-41d4-a716-446655440000",
  "file_size": 12345,
  "frame_count": 1,
  "dimensions": {
    "width": 256,
    "height": 256
  }
}
```

### 2. Convert Video
**POST** `/api/v1/convert/video`

Convert a video to animated `.spr` format.

**Form Parameters:**
- `file` (required): Video file
- `fps` (optional): Float (1-60), default 30.0
- `max_frames` (optional): Integer, limits total frames
- All sprite options from endpoint #1

**Response:** Same as endpoint #1

### 3. Convert Multiple Images (Animated)
**POST** `/api/v1/convert/images/animated`

Create an animated sprite from multiple images.

**Form Parameters:**
- `files` (required): Multiple image files
- `frame_interval` (optional): Float, time per frame in seconds, default 0.1
- All sprite options from endpoint #1

**Response:** Same as endpoint #1

### 4. Download Sprite
**GET** `/api/v1/download/{sprite_id}`

Download the generated sprite file.

**Response:** Binary `.spr` file

### 5. Delete Sprite
**DELETE** `/api/v1/delete/{sprite_id}`

Delete a generated sprite file.

**Response:**
```json
{
  "success": true,
  "message": "Sprite deleted successfully"
}
```

### 6. Health Check
**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

## Quick Start

### Local Development with Docker

1. **Clone/Download the project**
   ```bash
   cd sprite_api
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the API**
   - API: `https://cs16-sprite-api.onrender.com`
   - Interactive docs: `https://cs16-sprite-api.onrender.com/docs`
   - Alternative docs: `https://cs16-sprite-api.onrender.com/redoc`

### Manual Setup (Without Docker)

1. **Install Python 3.11+**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Deployment

### Deploy to Render

1. **Create a new Web Service** on [Render](https://render.com)

2. **Connect your repository**

3. **Configure the service:**
   - **Environment**: Docker
   - **Build Command**: (auto-detected from Dockerfile)
   - **Start Command**: (auto-detected from Dockerfile)
   - **Port**: 8000

4. **Add disk for persistent storage** (optional):
   - Mount path: `/app/outputs`
   - Size: 1GB+

5. **Deploy!**

### Deploy to Railway

1. **Create new project** on [Railway](https://railway.app)

2. **Deploy from GitHub** or use Railway CLI:
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Add environment variables** (if needed)

4. **Railway will auto-detect the Dockerfile and deploy**

### Deploy to Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly.io**
   ```bash
   fly auth login
   ```

3. **Launch the app**
   ```bash
   fly launch
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

### Deploy to Any Docker Host

1. **Build the image**
   ```bash
   docker build -t cs16-sprite-api .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -v ./outputs:/app/outputs \
     --name sprite-api \
     cs16-sprite-api
   ```

## Usage Examples

### cURL

**Convert an image:**
```bash
curl -X POST "https://cs16-sprite-api.onrender.com/api/v1/convert/image" \
  -F "file=@muzzleflash.png" \
  -F "texture_format=additive" \
  -F "sprite_type=vp_parallel"
```

**Download the sprite:**
```bash
curl -O -J "https://cs16-sprite-api.onrender.com/api/v1/download/{sprite_id}"
```

### Python

```python
import requests

# Convert image
with open('muzzleflash.png', 'rb') as f:
    files = {'file': f}
    data = {
        'texture_format': 'additive',
        'sprite_type': 'vp_parallel',
        'max_width': 128,
        'max_height': 128
    }
    
    response = requests.post(
        'https://cs16-sprite-api.onrender.com/api/v1/convert/image',
        files=files,
        data=data
    )
    
    result = response.json()
    sprite_id = result['sprite_id']
    
# Download sprite
download_response = requests.get(
    f'https://cs16-sprite-api.onrender.com/api/v1/download/{sprite_id}'
)

with open('muzzleflash.spr', 'wb') as f:
    f.write(download_response.content)
```

### JavaScript (Node.js)

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function convertToSprite() {
  const form = new FormData();
  form.append('file', fs.createReadStream('muzzleflash.png'));
  form.append('texture_format', 'additive');
  form.append('sprite_type', 'vp_parallel');
  
  const response = await axios.post(
    'https://cs16-sprite-api.onrender.com/api/v1/convert/image',
    form,
    { headers: form.getHeaders() }
  );
  
  const { sprite_id } = response.data;
  
  // Download
  const download = await axios.get(
    `https://cs16-sprite-api.onrender.com/api/v1/download/${sprite_id}`,
    { responseType: 'arraybuffer' }
  );
  
  fs.writeFileSync('muzzleflash.spr', download.data);
}
```

## Sprite Options Guide

### Sprite Type
- **vp_parallel_upright**: Always faces player, upright orientation (default for most effects)
- **facing_upright**: Faces player, stays upright (good for flames, smoke)
- **vp_parallel**: Always faces player, can rotate (good for explosions)
- **oriented**: Uses custom orientation (advanced)
- **vp_parallel_oriented**: Combination mode (advanced)

### Texture Format
- **normal**: Standard rendering (0% transparency on color 255)
- **additive**: Additive blending (glowing effects, muzzle flashes, explosions)
- **indexalpha**: Alpha from palette index (advanced)
- **alphatest**: Binary transparency (sharp edges)

### Sync Type
- **sync**: All sprites animate together
- **rand**: Random animation offset (more natural for multiple instances)

## Sprite Dimensions

- Must be multiples of 8 (8, 16, 24, 32, ..., 256, 512)
- Maximum recommended: 256x256 for compatibility
- Larger sprites consume more memory in-game

## Performance Notes

- **Video conversion**: Processing time depends on video length and FPS
- **Frame limit**: Consider using `max_frames` to limit video length
- **Recommended FPS**: 15-30 for smooth animation without excessive file size
- **Clean up**: Use DELETE endpoint to remove old sprites

## Environment Variables

Create a `.env` file for custom configuration:

```env
# Port (default: 8000)
PORT=8000

# Host (default: 0.0.0.0)
HOST=0.0.0.0

# Output directory (default: ./outputs)
OUTPUT_DIR=/app/outputs

# Temp directory (default: ./temp)
TEMP_DIR=/app/temp
```

## Troubleshooting

### Docker build fails
- Ensure you have enough disk space
- Try `docker system prune` to free up space

### Video conversion fails
- Ensure opencv-python is installed
- Check video codec compatibility
- Reduce FPS or use max_frames parameter

### Sprites don't work in CS 1.6
- Verify dimensions are multiples of 8
- Check sprite type matches your use case
- Ensure texture format is appropriate (additive for glows, normal for solids)

## License

Based on Valve's sprite generation tools. For educational and modding purposes.

## Contributing

Contributions welcome! Please ensure:
- Code follows PEP 8 style guide
- All endpoints return proper error messages
- Docker build succeeds
- README is updated for new features

## Support

For issues and questions:
- Check the `/docs` endpoint for interactive API documentation
- Review examples in this README
- Ensure your input files are in supported formats
