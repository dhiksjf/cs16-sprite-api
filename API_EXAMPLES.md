# API Usage Examples

Complete examples for using the CS 1.6 Sprite Generator API in various programming languages.

## Table of Contents
- [Python Examples](#python-examples)
- [JavaScript/Node.js Examples](#javascriptnodejs-examples)
- [cURL Examples](#curl-examples)
- [PHP Examples](#php-examples)
- [C# Examples](#c-examples)

---

## Python Examples

### Basic Image Conversion

```python
import requests

def convert_image_to_sprite(image_path, api_url="https://cs16-sprite-api.onrender.com"):
    """Convert an image to CS 1.6 sprite"""
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {
            'sprite_type': 'vp_parallel',
            'texture_format': 'additive',
            'max_width': 128,
            'max_height': 128
        }
        
        response = requests.post(
            f"{api_url}/api/v1/convert/image",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        sprite_id = result['sprite_id']
        
        # Download the sprite
        download_url = f"{api_url}{result['download_url']}"
        sprite_response = requests.get(download_url)
        
        # Save to file
        output_path = f"{sprite_id}.spr"
        with open(output_path, 'wb') as f:
            f.write(sprite_response.content)
        
        print(f"Sprite saved to: {output_path}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Usage
convert_image_to_sprite("muzzleflash.png")
```

### Video to Animated Sprite

```python
import requests

def convert_video_to_sprite(video_path, fps=15, max_frames=50, api_url="https://cs16-sprite-api.onrender.com"):
    """Convert a video to animated CS 1.6 sprite"""
    
    with open(video_path, 'rb') as f:
        files = {'file': f}
        data = {
            'sprite_type': 'vp_parallel',
            'texture_format': 'additive',
            'fps': fps,
            'max_frames': max_frames,
            'max_width': 128,
            'max_height': 128
        }
        
        response = requests.post(
            f"{api_url}/api/v1/convert/video",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Created sprite with {result['frame_count']} frames")
        
        # Download
        download_url = f"{api_url}{result['download_url']}"
        sprite_response = requests.get(download_url)
        
        output_path = f"explosion_{result['sprite_id']}.spr"
        with open(output_path, 'wb') as f:
            f.write(sprite_response.content)
        
        print(f"Sprite saved to: {output_path}")
        return result
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
convert_video_to_sprite("explosion.mp4", fps=20, max_frames=30)
```

### Multiple Images to Animated Sprite

```python
import requests

def create_animated_sprite(image_paths, frame_interval=0.1, api_url="https://cs16-sprite-api.onrender.com"):
    """Create animated sprite from multiple images"""
    
    files = [('files', open(path, 'rb')) for path in image_paths]
    data = {
        'sprite_type': 'vp_parallel',
        'texture_format': 'additive',
        'frame_interval': frame_interval,
        'max_width': 128,
        'max_height': 128
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/v1/convert/images/animated",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Download
            download_url = f"{api_url}{result['download_url']}"
            sprite_response = requests.get(download_url)
            
            output_path = "animated_sprite.spr"
            with open(output_path, 'wb') as f:
                f.write(sprite_response.content)
            
            print(f"Created animated sprite: {output_path}")
            return result
    finally:
        for _, f in files:
            f.close()

# Usage
images = ["frame1.png", "frame2.png", "frame3.png"]
create_animated_sprite(images)
```

---

## JavaScript/Node.js Examples

### Basic Image Conversion

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function convertImageToSprite(imagePath, apiUrl = 'https://cs16-sprite-api.onrender.com') {
  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(imagePath));
    form.append('sprite_type', 'vp_parallel');
    form.append('texture_format', 'additive');
    form.append('max_width', '128');
    form.append('max_height', '128');
    
    const response = await axios.post(
      `${apiUrl}/api/v1/convert/image`,
      form,
      { headers: form.getHeaders() }
    );
    
    const result = response.data;
    const spriteId = result.sprite_id;
    
    // Download the sprite
    const downloadResponse = await axios.get(
      `${apiUrl}${result.download_url}`,
      { responseType: 'arraybuffer' }
    );
    
    const outputPath = `${spriteId}.spr`;
    fs.writeFileSync(outputPath, downloadResponse.data);
    
    console.log(`Sprite saved to: ${outputPath}`);
    return result;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    return null;
  }
}

// Usage
convertImageToSprite('muzzleflash.png');
```

### Video Conversion

```javascript
async function convertVideoToSprite(videoPath, options = {}) {
  const {
    fps = 15,
    maxFrames = 50,
    apiUrl = 'https://cs16-sprite-api.onrender.com'
  } = options;
  
  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(videoPath));
    form.append('sprite_type', 'vp_parallel');
    form.append('texture_format', 'additive');
    form.append('fps', fps.toString());
    if (maxFrames) form.append('max_frames', maxFrames.toString());
    form.append('max_width', '128');
    form.append('max_height', '128');
    
    const response = await axios.post(
      `${apiUrl}/api/v1/convert/video`,
      form,
      { headers: form.getHeaders() }
    );
    
    const result = response.data;
    console.log(`Created sprite with ${result.frame_count} frames`);
    
    // Download
    const downloadResponse = await axios.get(
      `${apiUrl}${result.download_url}`,
      { responseType: 'arraybuffer' }
    );
    
    const outputPath = `explosion_${result.sprite_id}.spr`;
    fs.writeFileSync(outputPath, downloadResponse.data);
    
    console.log(`Sprite saved to: ${outputPath}`);
    return result;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    return null;
  }
}

// Usage
convertVideoToSprite('explosion.mp4', { fps: 20, maxFrames: 30 });
```

---

## cURL Examples

### Convert Image

```bash
curl -X POST "https://cs16-sprite-api.onrender.com/api/v1/convert/image" \
  -F "file=@muzzleflash.png" \
  -F "sprite_type=vp_parallel" \
  -F "texture_format=additive" \
  -F "max_width=128" \
  -F "max_height=128"
```

### Convert Video

```bash
curl -X POST "https://cs16-sprite-api.onrender.com/api/v1/convert/video" \
  -F "file=@explosion.mp4" \
  -F "sprite_type=vp_parallel" \
  -F "texture_format=additive" \
  -F "fps=20" \
  -F "max_frames=30" \
  -F "max_width=128" \
  -F "max_height=128"
```

### Download Sprite

```bash
# Get sprite_id from conversion response
curl -O -J "https://cs16-sprite-api.onrender.com/api/v1/download/{sprite_id}"
```

### Complete Workflow

```bash
# Convert
RESPONSE=$(curl -s -X POST "https://cs16-sprite-api.onrender.com/api/v1/convert/image" \
  -F "file=@muzzleflash.png" \
  -F "texture_format=additive")

# Extract sprite_id
SPRITE_ID=$(echo $RESPONSE | jq -r '.sprite_id')

# Download
curl -o "sprite.spr" "https://cs16-sprite-api.onrender.com/api/v1/download/$SPRITE_ID"

echo "Downloaded sprite.spr"
```

---

## PHP Examples

### Basic Conversion

```php
<?php

function convertImageToSprite($imagePath, $apiUrl = 'https://cs16-sprite-api.onrender.com') {
    $ch = curl_init();
    
    $postFields = [
        'file' => new CURLFile($imagePath),
        'sprite_type' => 'vp_parallel',
        'texture_format' => 'additive',
        'max_width' => 128,
        'max_height' => 128
    ];
    
    curl_setopt($ch, CURLOPT_URL, "$apiUrl/api/v1/convert/image");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200) {
        $result = json_decode($response, true);
        $spriteId = $result['sprite_id'];
        
        // Download sprite
        $spriteData = file_get_contents("$apiUrl{$result['download_url']}");
        file_put_contents("$spriteId.spr", $spriteData);
        
        echo "Sprite saved to: $spriteId.spr\n";
        return $result;
    } else {
        echo "Error: $httpCode\n$response\n";
        return null;
    }
}

// Usage
convertImageToSprite('muzzleflash.png');

?>
```

---

## C# Examples

### Using HttpClient

```csharp
using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;

public class SpriteConverter
{
    private readonly HttpClient _httpClient;
    private readonly string _apiUrl;
    
    public SpriteConverter(string apiUrl = "https://cs16-sprite-api.onrender.com")
    {
        _httpClient = new HttpClient();
        _apiUrl = apiUrl;
    }
    
    public async Task<string> ConvertImageToSprite(string imagePath)
    {
        using var content = new MultipartFormDataContent();
        
        // Add file
        var fileContent = new ByteArrayContent(File.ReadAllBytes(imagePath));
        content.Add(fileContent, "file", Path.GetFileName(imagePath));
        
        // Add parameters
        content.Add(new StringContent("vp_parallel"), "sprite_type");
        content.Add(new StringContent("additive"), "texture_format");
        content.Add(new StringContent("128"), "max_width");
        content.Add(new StringContent("128"), "max_height");
        
        var response = await _httpClient.PostAsync(
            $"{_apiUrl}/api/v1/convert/image",
            content
        );
        
        if (response.IsSuccessStatusCode)
        {
            var json = await response.Content.ReadAsStringAsync();
            dynamic result = Newtonsoft.Json.JsonConvert.DeserializeObject(json);
            
            string spriteId = result.sprite_id;
            
            // Download sprite
            var spriteData = await _httpClient.GetByteArrayAsync(
                $"{_apiUrl}{result.download_url}"
            );
            
            string outputPath = $"{spriteId}.spr";
            await File.WriteAllBytesAsync(outputPath, spriteData);
            
            Console.WriteLine($"Sprite saved to: {outputPath}");
            return spriteId;
        }
        else
        {
            Console.WriteLine($"Error: {response.StatusCode}");
            return null;
        }
    }
}

// Usage
var converter = new SpriteConverter();
await converter.ConvertImageToSprite("muzzleflash.png");
```

---

## Common Sprite Configurations

### Muzzle Flash
```json
{
  "sprite_type": "vp_parallel",
  "texture_format": "additive",
  "max_width": 128,
  "max_height": 128
}
```

### Explosion
```json
{
  "sprite_type": "vp_parallel",
  "texture_format": "additive",
  "max_width": 256,
  "max_height": 256
}
```

### Smoke
```json
{
  "sprite_type": "facing_upright",
  "texture_format": "alphatest",
  "max_width": 128,
  "max_height": 128
}
```

### Blood Splatter
```json
{
  "sprite_type": "oriented",
  "texture_format": "normal",
  "max_width": 64,
  "max_height": 64
}
```

### Laser Beam
```json
{
  "sprite_type": "oriented",
  "texture_format": "additive",
  "beam_length": 128,
  "max_width": 16,
  "max_height": 16
}
```
