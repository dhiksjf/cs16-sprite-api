"""
CS 1.6 Sprite Generator
Converts images and videos to .spr format for Counter-Strike 1.6
Based on Valve's sprite format specification
With Advanced AI-Powered Image Processing
"""

import struct
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import IntEnum
import numpy as np
from PIL import Image
import io

# Import advanced processor if available
try:
    from advanced_processor import AdvancedImageProcessor, ProcessingOptions, BackgroundRemovalMode, VideoFrameProcessor
    ADVANCED_PROCESSING_AVAILABLE = True
except ImportError:
    ADVANCED_PROCESSING_AVAILABLE = False
    AdvancedImageProcessor = None
    ProcessingOptions = None
    BackgroundRemovalMode = None
    VideoFrameProcessor = None


class SpriteType(IntEnum):
    """Sprite orientation types"""
    VP_PARALLEL_UPRIGHT = 0
    FACING_UPRIGHT = 1
    VP_PARALLEL = 2
    ORIENTED = 3
    VP_PARALLEL_ORIENTED = 4


class TextureFormat(IntEnum):
    """Sprite texture rendering formats"""
    NORMAL = 0
    ADDITIVE = 1
    INDEXALPHA = 2
    ALPHATEST = 3


class SyncType(IntEnum):
    """Frame synchronization types"""
    SYNC = 0
    RAND = 1


class FrameType(IntEnum):
    """Frame type (single or group)"""
    SINGLE = 0
    GROUP = 1


SPRITE_VERSION = 2
IDSPRITEHEADER = 0x49445350  # "IDSP" in little-endian


@dataclass
class SpriteFrame:
    """Represents a single sprite frame"""
    width: int
    height: int
    origin_x: int
    origin_y: int
    pixels: bytes
    interval: float = 0.1


@dataclass
class SpriteConfig:
    """Configuration for sprite generation"""
    sprite_type: SpriteType = SpriteType.VP_PARALLEL_UPRIGHT
    texture_format: TextureFormat = TextureFormat.ADDITIVE
    sync_type: SyncType = SyncType.RAND
    beam_length: float = 0.0
    use_16bit_palette: bool = True
    max_width: int = 256
    max_height: int = 256


class SpriteGenerator:
    """Generates CS 1.6 .spr files from images"""
    
    def __init__(self, config: SpriteConfig = None, processing_options: 'ProcessingOptions' = None):
        self.config = config or SpriteConfig()
        self.frames: List[SpriteFrame] = []
        self.palette: Optional[bytes] = None
        
        # Initialize advanced processor if available
        if ADVANCED_PROCESSING_AVAILABLE and processing_options:
            self.advanced_processor = AdvancedImageProcessor(processing_options)
        else:
            self.advanced_processor = None
        
    def _quantize_image(self, image: Image.Image) -> Tuple[Image.Image, bytes]:
        """Convert image to 256-color palette and extract palette"""
        # Convert to RGB if needed
        if image.mode == 'RGBA':
            # Create a white background for transparency
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Quantize to 256 colors
        quantized = image.quantize(colors=256, method=2)
        
        # Extract palette (RGB triplets)
        palette_data = quantized.getpalette()[:256*3]
        palette_bytes = bytes(palette_data)
        
        return quantized, palette_bytes
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image to fit max dimensions while maintaining aspect ratio"""
        width, height = image.size
        
        # Check if resize is needed
        if width > self.config.max_width or height > self.config.max_height:
            # Calculate scaling factor
            scale = min(self.config.max_width / width, self.config.max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Ensure dimensions are multiples of 8
            new_width = (new_width // 8) * 8
            new_height = (new_height // 8) * 8
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def _make_dimensions_valid(self, width: int, height: int) -> Tuple[int, int]:
        """Ensure dimensions are multiples of 8 and within limits"""
        width = min((width // 8) * 8, self.config.max_width)
        height = min((height // 8) * 8, self.config.max_height)
        return max(8, width), max(8, height)
    
    def add_frame_from_image(self, image: Image.Image, interval: float = 0.1,
                            origin_x: Optional[int] = None, origin_y: Optional[int] = None):
        """Add a frame from a PIL Image"""
        # Apply advanced processing if enabled
        if self.advanced_processor:
            image = self.advanced_processor.process_image(image)
        
        # Resize if needed
        image = self._resize_image(image)
        
        # Ensure valid dimensions
        width, height = self._make_dimensions_valid(image.width, image.height)
        
        if image.size != (width, height):
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        # Quantize and get palette
        quantized, palette = self._quantize_image(image)
        
        # Store palette from first frame
        if self.palette is None:
            self.palette = palette
        
        # Get pixel data
        pixels = bytes(quantized.tobytes())
        
        # Calculate origin (center by default)
        if origin_x is None:
            origin_x = -(width // 2)
        if origin_y is None:
            origin_y = height // 2
        
        frame = SpriteFrame(
            width=width,
            height=height,
            origin_x=origin_x,
            origin_y=origin_y,
            pixels=pixels,
            interval=interval
        )
        
        self.frames.append(frame)
    
    def add_frame_from_file(self, filepath: str, interval: float = 0.1,
                           origin_x: Optional[int] = None, origin_y: Optional[int] = None):
        """Add a frame from an image file"""
        image = Image.open(filepath)
        self.add_frame_from_image(image, interval, origin_x, origin_y)
    
    def add_frame_from_bytes(self, image_bytes: bytes, interval: float = 0.1,
                            origin_x: Optional[int] = None, origin_y: Optional[int] = None):
        """Add a frame from image bytes"""
        image = Image.open(io.BytesIO(image_bytes))
        self.add_frame_from_image(image, interval, origin_x, origin_y)
    
    def _calculate_bounding_radius(self) -> float:
        """Calculate bounding radius from max frame dimensions"""
        if not self.frames:
            return 0.0
        
        max_width = max(frame.width for frame in self.frames)
        max_height = max(frame.height for frame in self.frames)
        
        return math.sqrt((max_width / 2) ** 2 + (max_height / 2) ** 2)
    
    def _write_little_endian_int(self, value: int) -> bytes:
        """Write 32-bit little-endian integer"""
        return struct.pack('<i', value)
    
    def _write_little_endian_float(self, value: float) -> bytes:
        """Write 32-bit little-endian float"""
        return struct.pack('<f', value)
    
    def generate(self) -> bytes:
        """Generate the .spr file as bytes"""
        if not self.frames:
            raise ValueError("No frames added to sprite")
        
        if self.palette is None:
            raise ValueError("No palette available")
        
        output = io.BytesIO()
        
        # Calculate max dimensions
        max_width = max(frame.width for frame in self.frames)
        max_height = max(frame.height for frame in self.frames)
        bounding_radius = self._calculate_bounding_radius()
        
        # Write header
        output.write(self._write_little_endian_int(IDSPRITEHEADER))
        output.write(self._write_little_endian_int(SPRITE_VERSION))
        output.write(self._write_little_endian_int(self.config.sprite_type))
        output.write(self._write_little_endian_int(self.config.texture_format))
        output.write(self._write_little_endian_float(bounding_radius))
        output.write(self._write_little_endian_int(max_width))
        output.write(self._write_little_endian_int(max_height))
        output.write(self._write_little_endian_int(len(self.frames)))
        output.write(self._write_little_endian_float(self.config.beam_length))
        output.write(self._write_little_endian_float(float(self.config.sync_type)))
        
        # Write palette if 16-bit mode
        if self.config.use_16bit_palette:
            output.write(struct.pack('<H', 256))  # Palette size
            output.write(self.palette)
        
        # Write frames (all as single frames for simplicity)
        for frame in self.frames:
            # Write frame type
            output.write(self._write_little_endian_int(FrameType.SINGLE))
            
            # Write frame header
            output.write(self._write_little_endian_int(frame.origin_x))
            output.write(self._write_little_endian_int(frame.origin_y))
            output.write(self._write_little_endian_int(frame.width))
            output.write(self._write_little_endian_int(frame.height))
            
            # Write pixel data
            output.write(frame.pixels)
        
        return output.getvalue()
    
    def save(self, filepath: str):
        """Save sprite to file"""
        sprite_data = self.generate()
        with open(filepath, 'wb') as f:
            f.write(sprite_data)
    
    def clear(self):
        """Clear all frames and palette"""
        self.frames.clear()
        self.palette = None


class VideoSpriteGenerator:
    """Converts video files to animated sprites"""
    
    def __init__(self, config: SpriteConfig = None, processing_options: 'ProcessingOptions' = None):
        self.config = config or SpriteConfig()
        self.processing_options = processing_options
    
    def extract_frames_from_video(self, video_path: str, fps: Optional[float] = None,
                                  max_frames: Optional[int] = None) -> List[Image.Image]:
        """Extract frames from video file"""
        # Use advanced processor if available and configured
        if ADVANCED_PROCESSING_AVAILABLE and self.processing_options:
            image_processor = AdvancedImageProcessor(self.processing_options)
            video_processor = VideoFrameProcessor(image_processor)
            return video_processor.extract_and_process_frames(video_path, fps or 30.0, max_frames)
        
        # Fall back to basic extraction
        try:
            import cv2
        except ImportError:
            raise ImportError("opencv-python is required for video processing. Install it with: pip install opencv-python")
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame skip for desired FPS
        if fps is None:
            fps = min(video_fps, 30)  # Default to max 30 FPS
        
        frame_skip = max(1, int(video_fps / fps))
        
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
                
                if max_frames and len(frames) >= max_frames:
                    break
            
            frame_count += 1
        
        cap.release()
        return frames
    
    def generate_from_video(self, video_path: str, fps: Optional[float] = None,
                           max_frames: Optional[int] = None) -> bytes:
        """Generate sprite from video file"""
        frames = self.extract_frames_from_video(video_path, fps, max_frames)
        
        if not frames:
            raise ValueError("No frames extracted from video")
        
        generator = SpriteGenerator(self.config, self.processing_options)
        
        # Calculate interval based on FPS
        if fps is None:
            fps = 30
        interval = 1.0 / fps
        
        for frame in frames:
            generator.add_frame_from_image(frame, interval=interval)
        
        return generator.generate()
