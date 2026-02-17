"""
Advanced Image Processor for CS 1.6 Sprites
AI-powered image and video processing with automatic enhancements
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageChops, ImageDraw
from typing import Tuple, Optional, List
import cv2
from dataclasses import dataclass
from enum import Enum


class BackgroundRemovalMode(Enum):
    """Background removal modes"""
    AUTO = "auto"  # Detect and remove automatically
    BLACK = "black"  # Remove black background
    WHITE = "white"  # Remove white background
    GREEN = "green"  # Remove green screen (chroma key)
    CUSTOM = "custom"  # Custom color removal


@dataclass
class ProcessingOptions:
    """Advanced processing options"""
    # Background removal
    remove_background: bool = False
    background_mode: BackgroundRemovalMode = BackgroundRemovalMode.AUTO
    background_color: Optional[Tuple[int, int, int]] = None
    background_threshold: int = 30  # Color tolerance
    
    # Auto-enhancement
    auto_enhance: bool = False
    enhance_brightness: float = 1.0  # 1.0 = no change
    enhance_contrast: float = 1.0
    enhance_sharpness: float = 1.0
    enhance_color: float = 1.0
    
    # Smart cropping
    auto_crop: bool = False
    crop_threshold: int = 10  # Pixel intensity threshold
    crop_padding: int = 5  # Padding around content
    
    # Edge processing
    smooth_edges: bool = False
    edge_blur_radius: int = 2
    
    # Noise reduction
    denoise: bool = False
    denoise_strength: int = 5
    
    # Color correction
    auto_color_balance: bool = False
    gamma_correction: float = 1.0
    
    # Content detection
    center_content: bool = False
    detect_motion: bool = False  # For video frames
    
    # Frame optimization (video)
    remove_duplicate_frames: bool = False
    duplicate_threshold: float = 0.95  # Similarity threshold
    stabilize_frames: bool = False


class AdvancedImageProcessor:
    """Advanced image processing with AI-powered features"""
    
    def __init__(self, options: ProcessingOptions = None):
        self.options = options or ProcessingOptions()
    
    def process_image(self, image: Image.Image) -> Image.Image:
        """Apply all enabled processing to an image"""
        # Ensure RGBA mode for transparency
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Remove background first if enabled
        if self.options.remove_background:
            image = self.remove_background(image)
        
        # Auto-crop empty space
        if self.options.auto_crop:
            image = self.auto_crop(image)
        
        # Denoise
        if self.options.denoise:
            image = self.denoise_image(image)
        
        # Auto-enhance
        if self.options.auto_enhance:
            image = self.auto_enhance(image)
        
        # Smooth edges
        if self.options.smooth_edges:
            image = self.smooth_edges(image)
        
        # Color correction
        if self.options.auto_color_balance:
            image = self.auto_color_balance(image)
        
        # Gamma correction
        if self.options.gamma_correction != 1.0:
            image = self.apply_gamma(image, self.options.gamma_correction)
        
        # Center content
        if self.options.center_content:
            image = self.center_content(image)
        
        return image
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background using various methods"""
        if self.options.background_mode == BackgroundRemovalMode.AUTO:
            return self._remove_background_auto(image)
        elif self.options.background_mode == BackgroundRemovalMode.BLACK:
            return self._remove_color(image, (0, 0, 0))
        elif self.options.background_mode == BackgroundRemovalMode.WHITE:
            return self._remove_color(image, (255, 255, 255))
        elif self.options.background_mode == BackgroundRemovalMode.GREEN:
            return self._remove_green_screen(image)
        elif self.options.background_mode == BackgroundRemovalMode.CUSTOM:
            if self.options.background_color:
                return self._remove_color(image, self.options.background_color)
        
        return image
    
    def _remove_background_auto(self, image: Image.Image) -> Image.Image:
        """Automatically detect and remove background"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Get corner pixels to determine background color
        corners = [
            img_array[0, 0],
            img_array[0, -1],
            img_array[-1, 0],
            img_array[-1, -1]
        ]
        
        # Find most common corner color
        bg_color = np.median(corners, axis=0).astype(int)[:3]
        
        # Remove that color
        return self._remove_color(image, tuple(bg_color))
    
    def _remove_color(self, image: Image.Image, color: Tuple[int, int, int]) -> Image.Image:
        """Remove a specific color with tolerance"""
        img_array = np.array(image)
        
        # Split into RGB and alpha
        rgb = img_array[:, :, :3]
        
        # Create alpha channel if doesn't exist
        if img_array.shape[2] == 3:
            alpha = np.full((img_array.shape[0], img_array.shape[1]), 255, dtype=np.uint8)
        else:
            alpha = img_array[:, :, 3]
        
        # Calculate color distance
        color_array = np.array(color)
        distance = np.sqrt(np.sum((rgb - color_array) ** 2, axis=2))
        
        # Set alpha based on distance
        threshold = self.options.background_threshold
        alpha[distance < threshold] = 0
        
        # Smooth transition at edges
        transition_mask = (distance >= threshold) & (distance < threshold * 2)
        alpha[transition_mask] = ((distance[transition_mask] - threshold) / threshold * 255).astype(np.uint8)
        
        # Combine back
        result = np.dstack([rgb, alpha])
        return Image.fromarray(result, 'RGBA')
    
    def _remove_green_screen(self, image: Image.Image) -> Image.Image:
        """Remove green screen (chroma keying)"""
        img_array = np.array(image)
        rgb = img_array[:, :, :3]
        
        # Convert to HSV for better green detection
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        
        # Define range for green color
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        
        # Create mask
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Invert mask (we want to keep non-green)
        mask = cv2.bitwise_not(mask)
        
        # Smooth mask edges
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Create alpha channel
        if img_array.shape[2] == 4:
            alpha = img_array[:, :, 3]
            alpha = np.minimum(alpha, mask)
        else:
            alpha = mask
        
        result = np.dstack([rgb, alpha])
        return Image.fromarray(result, 'RGBA')
    
    def auto_crop(self, image: Image.Image) -> Image.Image:
        """Automatically crop to content bounds"""
        # Convert to numpy
        img_array = np.array(image)
        
        # Get alpha channel if exists, otherwise use luminance
        if img_array.shape[2] == 4:
            mask = img_array[:, :, 3]
        else:
            # Convert to grayscale for content detection
            gray = np.mean(img_array[:, :, :3], axis=2)
            mask = (gray > self.options.crop_threshold).astype(np.uint8) * 255
        
        # Find content bounds
        rows = np.any(mask > self.options.crop_threshold, axis=1)
        cols = np.any(mask > self.options.crop_threshold, axis=0)
        
        if not np.any(rows) or not np.any(cols):
            return image  # No content found
        
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        # Add padding
        padding = self.options.crop_padding
        y_min = max(0, y_min - padding)
        y_max = min(img_array.shape[0], y_max + padding + 1)
        x_min = max(0, x_min - padding)
        x_max = min(img_array.shape[1], x_max + padding + 1)
        
        # Crop
        return image.crop((x_min, y_min, x_max, y_max))
    
    def auto_enhance(self, image: Image.Image) -> Image.Image:
        """Automatically enhance image quality"""
        # Brightness
        if self.options.enhance_brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.options.enhance_brightness)
        
        # Contrast
        if self.options.enhance_contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.options.enhance_contrast)
        
        # Sharpness
        if self.options.enhance_sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.options.enhance_sharpness)
        
        # Color
        if self.options.enhance_color != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(self.options.enhance_color)
        
        return image
    
    def smooth_edges(self, image: Image.Image) -> Image.Image:
        """Smooth edges with anti-aliasing"""
        # Apply Gaussian blur to alpha channel only
        img_array = np.array(image)
        
        if img_array.shape[2] == 4:
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # Blur alpha channel
            alpha_blurred = cv2.GaussianBlur(alpha, (0, 0), self.options.edge_blur_radius)
            
            result = np.dstack([rgb, alpha_blurred])
            return Image.fromarray(result, 'RGBA')
        
        return image
    
    def denoise_image(self, image: Image.Image) -> Image.Image:
        """Reduce noise in image"""
        img_array = np.array(image)
        
        # Apply non-local means denoising
        if img_array.shape[2] == 4:
            rgb = img_array[:, :, :3]
            alpha = img_array[:, :, 3]
            
            # Denoise RGB channels
            rgb_denoised = cv2.fastNlMeansDenoisingColored(
                rgb, None, 
                self.options.denoise_strength, 
                self.options.denoise_strength,
                7, 21
            )
            
            result = np.dstack([rgb_denoised, alpha])
        else:
            result = cv2.fastNlMeansDenoisingColored(
                img_array, None,
                self.options.denoise_strength,
                self.options.denoise_strength,
                7, 21
            )
        
        return Image.fromarray(result, 'RGBA' if img_array.shape[2] == 4 else 'RGB')
    
    def auto_color_balance(self, image: Image.Image) -> Image.Image:
        """Automatic color balance"""
        img_array = np.array(image)
        
        if img_array.shape[2] >= 3:
            rgb = img_array[:, :, :3]
            
            # Calculate channel means
            means = np.mean(rgb, axis=(0, 1))
            
            # Target mean (gray)
            target = np.mean(means)
            
            # Adjust each channel
            for i in range(3):
                if means[i] > 0:
                    rgb[:, :, i] = np.clip(rgb[:, :, i] * (target / means[i]), 0, 255).astype(np.uint8)
            
            if img_array.shape[2] == 4:
                result = np.dstack([rgb, img_array[:, :, 3]])
            else:
                result = rgb
            
            return Image.fromarray(result, 'RGBA' if img_array.shape[2] == 4 else 'RGB')
        
        return image
    
    def apply_gamma(self, image: Image.Image, gamma: float) -> Image.Image:
        """Apply gamma correction"""
        img_array = np.array(image)
        
        # Build lookup table
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
        
        # Apply to RGB channels only
        if img_array.shape[2] >= 3:
            rgb = cv2.LUT(img_array[:, :, :3], table)
            
            if img_array.shape[2] == 4:
                result = np.dstack([rgb, img_array[:, :, 3]])
            else:
                result = rgb
            
            return Image.fromarray(result, 'RGBA' if img_array.shape[2] == 4 else 'RGB')
        
        return image
    
    def center_content(self, image: Image.Image) -> Image.Image:
        """Center content in frame"""
        # Get content center
        img_array = np.array(image)
        
        if img_array.shape[2] == 4:
            mask = img_array[:, :, 3]
        else:
            gray = np.mean(img_array[:, :, :3], axis=2)
            mask = (gray > 10).astype(np.uint8) * 255
        
        # Find center of mass
        moments = cv2.moments(mask)
        
        if moments['m00'] == 0:
            return image
        
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
        
        # Calculate shift to center
        img_center_x = img_array.shape[1] // 2
        img_center_y = img_array.shape[0] // 2
        
        shift_x = img_center_x - cx
        shift_y = img_center_y - cy
        
        # Translate image
        translation_matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        
        if img_array.shape[2] == 4:
            result = cv2.warpAffine(
                img_array, translation_matrix,
                (img_array.shape[1], img_array.shape[0]),
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )
            return Image.fromarray(result, 'RGBA')
        else:
            result = cv2.warpAffine(
                img_array, translation_matrix,
                (img_array.shape[1], img_array.shape[0]),
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0)
            )
            return Image.fromarray(result, 'RGB')
    
    def detect_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Detect motion between two frames (returns difference score)"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
        
        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Calculate mean difference (normalized)
        motion_score = np.mean(diff) / 255.0
        
        return motion_score
    
    def are_frames_similar(self, frame1: Image.Image, frame2: Image.Image) -> bool:
        """Check if two frames are similar (for deduplication)"""
        # Resize for faster comparison
        size = (64, 64)
        img1 = frame1.resize(size)
        img2 = frame2.resize(size)
        
        # Convert to arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Calculate similarity
        diff = np.abs(arr1.astype(float) - arr2.astype(float))
        similarity = 1.0 - (np.mean(diff) / 255.0)
        
        return similarity >= self.options.duplicate_threshold


class VideoFrameProcessor:
    """Process video frames with advanced features"""
    
    def __init__(self, image_processor: AdvancedImageProcessor):
        self.image_processor = image_processor
        self.options = image_processor.options
    
    def extract_and_process_frames(self, video_path: str, fps: float = 30.0,
                                   max_frames: Optional[int] = None) -> List[Image.Image]:
        """Extract and process video frames with advanced features"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_skip = max(1, int(video_fps / fps))
        
        frames = []
        frame_count = 0
        previous_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_frame = Image.fromarray(frame_rgb)
                
                # Check for duplicate frames
                if self.options.remove_duplicate_frames and previous_frame is not None:
                    if self.image_processor.are_frames_similar(pil_frame, previous_frame):
                        frame_count += 1
                        continue
                
                # Process frame
                processed_frame = self.image_processor.process_image(pil_frame)
                
                frames.append(processed_frame)
                previous_frame = processed_frame
                
                if max_frames and len(frames) >= max_frames:
                    break
            
            frame_count += 1
        
        cap.release()
        
        # Stabilize frames if enabled
        if self.options.stabilize_frames and len(frames) > 1:
            frames = self._stabilize_frames(frames)
        
        return frames
    
    def _stabilize_frames(self, frames: List[Image.Image]) -> List[Image.Image]:
        """Stabilize video frames"""
        # Simple stabilization by aligning content centers
        stabilized = []
        
        # Use first frame as reference
        reference = frames[0]
        stabilized.append(reference)
        
        for i in range(1, len(frames)):
            # For now, just add the frame
            # More advanced stabilization can be added using optical flow
            stabilized.append(frames[i])
        
        return stabilized
