# 🚀 ADVANCED FEATURES GUIDE

## AI-Powered Image & Video Processing

The CS 1.6 Sprite Generator API v2.0 includes powerful AI-driven features that automatically enhance your images and videos for optimal sprite quality.

---

## 🎨 Features Overview

### 1. **Automatic Background Removal**
Remove backgrounds automatically with multiple detection modes.

**Modes:**
- `auto` - Automatically detect and remove background
- `black` - Remove black backgrounds (perfect for effects)
- `white` - Remove white backgrounds
- `green` - Chroma key (green screen removal)
- `custom` - Remove specific color
- `none` - No background removal

**Parameters:**
- `remove_background` (bool): Enable/disable
- `background_mode` (string): Detection mode
- `background_threshold` (int 0-255): Color tolerance (default: 30)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@muzzleflash.png" \
  -F "remove_background=true" \
  -F "background_mode=black" \
  -F "background_threshold=30"
```

---

### 2. **Smart Auto-Cropping**
Automatically crop images to content bounds, removing empty space.

**Features:**
- Detects content boundaries
- Removes transparent/empty areas
- Adds customizable padding
- Preserves aspect ratio

**Parameters:**
- `auto_crop` (bool): Enable auto-cropping
- `crop_padding` (int 0-50): Padding around content (default: 5)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@sprite.png" \
  -F "auto_crop=true" \
  -F "crop_padding=10"
```

---

### 3. **Image Enhancement**
Automatically enhance image quality with professional adjustments.

**Controls:**
- `enhance_brightness` (0.1-3.0): Adjust brightness (1.0 = no change)
- `enhance_contrast` (0.1-3.0): Adjust contrast (1.0 = no change)
- `enhance_sharpness` (0.1-3.0): Adjust sharpness (1.0 = no change)

**Parameters:**
- `auto_enhance` (bool): Enable enhancement
- Individual control sliders for each aspect

**Example:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v2/convert/advanced',
    files={'file': open('explosion.png', 'rb')},
    data={
        'auto_enhance': True,
        'enhance_brightness': 1.2,
        'enhance_contrast': 1.3,
        'enhance_sharpness': 1.5
    }
)
```

---

### 4. **Edge Smoothing**
Apply anti-aliasing and smooth edges for professional quality.

**Features:**
- Gaussian blur on edges
- Anti-aliasing
- Smooth transparency transitions
- Configurable blur radius

**Parameters:**
- `smooth_edges` (bool): Enable edge smoothing
- `edge_blur_radius` (int 1-10): Smoothing intensity (default: 2)

**Example:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('smooth_edges', 'true');
formData.append('edge_blur_radius', '3');

fetch('http://localhost:8000/api/v2/convert/advanced', {
    method: 'POST',
    body: formData
});
```

---

### 5. **Noise Reduction**
Remove grain and noise from images and videos.

**Features:**
- Non-local means denoising
- Preserves image details
- Fast processing
- Adjustable strength

**Parameters:**
- `denoise` (bool): Enable noise reduction
- `denoise_strength` (int 1-20): Strength (default: 5)

**Best For:**
- Low-light footage
- Compressed videos
- Scanned images
- Old footage

---

### 6. **Color Correction**
Automatic color balance and gamma adjustment.

**Features:**
- Auto white balance
- Gamma correction
- Color temperature adjustment
- Exposure correction

**Parameters:**
- `auto_color_balance` (bool): Auto balance colors
- `gamma_correction` (float 0.1-3.0): Gamma value (1.0 = no change)

**Example:**
```python
# Brighten dark sprites
data = {
    'auto_color_balance': True,
    'gamma_correction': 1.3  # Lighter
}

# Darken bright sprites
data = {
    'gamma_correction': 0.8  # Darker
}
```

---

### 7. **Content Centering**
Automatically center content within the frame.

**Features:**
- Detects content center of mass
- Aligns to frame center
- Maintains transparency
- Perfect for symmetric sprites

**Parameters:**
- `center_content` (bool): Enable centering

**Perfect For:**
- Icons
- Centered effects
- Symmetrical sprites
- UI elements

---

### 8. **Video Frame Optimization**
Remove duplicate frames and optimize video sprites.

**Features:**
- Duplicate frame detection
- Similarity-based removal
- Motion detection
- Frame stabilization

**Parameters:**
- `remove_duplicate_frames` (bool): Enable deduplication
- `duplicate_threshold` (float 0.0-1.0): Similarity threshold (default: 0.95)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@explosion.mp4" \
  -F "is_video=true" \
  -F "remove_duplicate_frames=true" \
  -F "duplicate_threshold=0.95" \
  -F "fps=20"
```

---

## 🎯 Common Use Cases

### Muzzle Flash (Black Background)
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@muzzleflash.png" \
  -F "remove_background=true" \
  -F "background_mode=black" \
  -F "auto_crop=true" \
  -F "smooth_edges=true" \
  -F "center_content=true" \
  -F "texture_format=additive"
```

### Explosion Video
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@explosion.mp4" \
  -F "is_video=true" \
  -F "fps=20" \
  -F "max_frames=30" \
  -F "remove_background=true" \
  -F "background_mode=black" \
  -F "auto_enhance=true" \
  -F "enhance_brightness=1.2" \
  -F "remove_duplicate_frames=true" \
  -F "texture_format=additive"
```

### Green Screen Effect
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@greenscreen.mp4" \
  -F "is_video=true" \
  -F "fps=15" \
  -F "remove_background=true" \
  -F "background_mode=green" \
  -F "smooth_edges=true" \
  -F "texture_format=alphatest"
```

### Scanned Image Cleanup
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@scanned_sprite.jpg" \
  -F "denoise=true" \
  -F "denoise_strength=10" \
  -F "auto_enhance=true" \
  -F "enhance_contrast=1.3" \
  -F "enhance_sharpness=1.5" \
  -F "auto_crop=true"
```

---

## 📊 Python Examples

### Complete Advanced Conversion
```python
import requests

def advanced_sprite_conversion(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {
            # Sprite settings
            'sprite_type': 'vp_parallel',
            'texture_format': 'additive',
            'max_width': 128,
            'max_height': 128,
            
            # Background removal
            'remove_background': True,
            'background_mode': 'black',
            'background_threshold': 30,
            
            # Enhancement
            'auto_enhance': True,
            'enhance_brightness': 1.2,
            'enhance_contrast': 1.1,
            'enhance_sharpness': 1.3,
            
            # Processing
            'auto_crop': True,
            'crop_padding': 5,
            'smooth_edges': True,
            'edge_blur_radius': 2,
            'center_content': True,
        }
        
        response = requests.post(
            'http://localhost:8000/api/v2/convert/advanced',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Created sprite: {result['filename']}")
            print(f"📊 Frames: {result['frame_count']}")
            print(f"📏 Size: {result['dimensions']}")
            print(f"🎨 Processing: {result['processing_applied']}")
            
            # Download sprite
            sprite_id = result['sprite_id']
            sprite_data = requests.get(
                f"http://localhost:8000/api/v1/download/{sprite_id}"
            )
            
            with open(f"output_{sprite_id}.spr", 'wb') as out:
                out.write(sprite_data.content)
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None

# Usage
advanced_sprite_conversion('muzzleflash.png')
```

### Video with All Features
```python
def advanced_video_conversion(video_path):
    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {
            # Video settings
            'is_video': True,
            'fps': 20,
            'max_frames': 30,
            
            # All advanced features
            'remove_background': True,
            'background_mode': 'black',
            'auto_enhance': True,
            'enhance_brightness': 1.3,
            'auto_crop': True,
            'smooth_edges': True,
            'denoise': True,
            'denoise_strength': 5,
            'center_content': True,
            'remove_duplicate_frames': True,
            'duplicate_threshold': 0.95,
            
            # Sprite settings
            'texture_format': 'additive',
            'max_width': 128,
            'max_height': 128,
        }
        
        response = requests.post(
            'http://localhost:8000/api/v2/convert/advanced',
            files=files,
            data=data
        )
        
        return response.json()

# Usage
result = advanced_video_conversion('explosion.mp4')
```

---

## 🎮 Recommended Settings by Use Case

### 🔥 Explosions & Fire
```python
{
    'remove_background': True,
    'background_mode': 'black',
    'auto_enhance': True,
    'enhance_brightness': 1.2,
    'enhance_contrast': 1.2,
    'smooth_edges': True,
    'center_content': True,
    'texture_format': 'additive'
}
```

### ⚡ Muzzle Flashes
```python
{
    'remove_background': True,
    'background_mode': 'black',
    'auto_crop': True,
    'smooth_edges': True,
    'auto_enhance': True,
    'enhance_brightness': 1.3,
    'texture_format': 'additive'
}
```

### 💨 Smoke & Particles
```python
{
    'remove_background': True,
    'background_mode': 'auto',
    'smooth_edges': True,
    'edge_blur_radius': 3,
    'denoise': True,
    'texture_format': 'alphatest'
}
```

### 🩸 Blood Effects
```python
{
    'remove_background': True,
    'background_mode': 'white',
    'auto_crop': True,
    'enhance_color': 1.2,
    'texture_format': 'normal'
}
```

### 🎬 Green Screen
```python
{
    'remove_background': True,
    'background_mode': 'green',
    'smooth_edges': True,
    'denoise': True,
    'remove_duplicate_frames': True,
    'texture_format': 'alphatest'
}
```

---

## ⚡ Performance Tips

1. **Background Removal**: Use specific modes (black/white/green) instead of 'auto' for faster processing
2. **Frame Limit**: Set `max_frames` for videos to control processing time
3. **Duplicate Removal**: Enable for video footage to reduce file size
4. **Denoise**: Only enable for noisy footage (adds processing time)
5. **Crop First**: Auto-crop before other processing for better performance

---

## 🔧 Troubleshooting

### Background Not Removed Properly
- Increase `background_threshold` (try 40-50)
- Try specific mode (black/white/green) instead of auto
- Ensure background is uniform color

### Edges Look Jagged
- Enable `smooth_edges`
- Increase `edge_blur_radius` to 3-4
- Try higher resolution source

### Image Too Dark/Bright
- Adjust `gamma_correction` (>1.0 lighter, <1.0 darker)
- Enable `auto_enhance`
- Adjust `enhance_brightness`

### Video Too Large
- Enable `remove_duplicate_frames`
- Reduce `fps`
- Set `max_frames` limit
- Reduce `max_width` and `max_height`

### Processing Too Slow
- Disable `denoise` if not needed
- Use lower `max_frames`
- Reduce resolution
- Disable unnecessary features

---

## 📈 Before/After Comparisons

### Without Advanced Processing:
- Rough edges
- Background included
- Off-center content
- Noise and artifacts
- Poor contrast

### With Advanced Processing:
- ✅ Smooth, anti-aliased edges
- ✅ Clean transparent background
- ✅ Perfectly centered
- ✅ Clean, noise-free
- ✅ Enhanced colors and contrast
- ✅ Optimized file size

---

## 🌟 Best Practices

1. **Always enable background removal** for effects with solid backgrounds
2. **Use auto-crop** to minimize sprite size
3. **Enable smooth_edges** for professional quality
4. **Center content** for symmetric effects
5. **Remove duplicates** from video footage
6. **Enhance conservatively** - use 1.1-1.3 multipliers
7. **Test different background modes** if auto doesn't work
8. **Denoise only when needed** - it adds processing time

---

## 🚀 Getting Started

1. **Basic Usage:**
```bash
curl -X POST "http://localhost:8000/api/v2/convert/advanced" \
  -F "file=@image.png" \
  -F "remove_background=true"
```

2. **Try Interactive Docs:**
Visit `http://localhost:8000/docs` and test the `/api/v2/convert/advanced` endpoint

3. **Check Features:**
```bash
curl http://localhost:8000/api/v1/features
```

---

**Ready to create professional CS 1.6 sprites with AI-powered processing!** 🎮✨
